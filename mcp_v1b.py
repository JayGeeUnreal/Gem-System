# ==============================================================================
#                      Master Control Program (mcp.py)
#          - UNIFIED MULTIMODAL & PIPELINED ARCHITECTURE -
# ==============================================================================
# This script acts as the central brain for the AI system. It includes:
# - A unified multimodal mode ('ollama_vision') for models like Llava/Gemma.
# - Pipelined modes ('ollama', 'gemini') for text-only LLMs.
# - A THREAD-SAFE unified RAG( ChromaDB) memory system with a robust, manual loader for the
#   RAG using chromaDb
# - Location awareness, OSC command bypass, multi-platform broadcasting & more.
# ==============================================================================
import requests
import json
import configparser
import sys
import os
import platform
import google.generativeai as genai
import re
import datetime
import chromadb
from collections import deque
from pythonosc import udp_client, osc_message_builder

from flask import Flask, request, jsonify
from flask_cors import CORS

# --- 1. CONFIGURATION LOADING ---
# ------------------------------------------------------------------------------
def load_config():
    """Loads all settings from the mcp_settings.ini file."""
    config_file = 'mcp_settings.ini'
    config = configparser.ConfigParser()
    if not os.path.exists(config_file): sys.exit(f"FATAL ERROR: Config file '{config_file}' not found.")
    config.read(config_file)
    settings = {}
    try:
        settings['system_prompt'] = config.get('SystemPrompt', 'prompt', fallback='').strip()
        settings['llm_choice'] = config.get('MCP', 'llm_choice')
        settings['host'] = config.get('MCP', 'host')
        settings['port'] = config.getint('MCP', 'port')
        settings['max_response_length'] = config.getint('Assistant', 'max_response_length', fallback=0)
        raw_wake_words = config.get('Assistant', 'wake_words', fallback='')
        settings['wake_words'] = [word.strip().lower() for word in raw_wake_words.split(',') if word.strip()]
        raw_command_verbs = config.get('Assistant', 'command_verbs', fallback='')
        settings['command_verbs'] = [verb.strip().lower() for verb in raw_command_verbs.split(',') if verb.strip()]
        settings['vision_service_scan_url'] = config.get('VisionService', 'scan_url')
        settings['vision_service_get_image_url'] = config.get('VisionService', 'vision_service_get_image_url', fallback='')
        raw_triggers = config.get('VisionService', 'vision_trigger_words', fallback='')
        settings['vision_trigger_words'] = [word.strip().lower() for word in raw_triggers.split(',') if word.strip()]
        settings['social_stream_enabled'] = config.getboolean('SocialStream', 'enabled', fallback=False)
        settings['social_stream_session_id'] = config.get('SocialStream', 'session_id')
        raw_platforms = config.get('SocialStream', 'target_platforms', fallback='')
        settings['social_stream_targets'] = [p.strip() for p in raw_platforms.split(',') if p.strip()]
        settings['social_stream_api_url'] = config.get('SocialStream', 'api_url')
        settings['styletts_enabled'] = config.getboolean('StyleTTS', 'enabled', fallback=False)
        settings['styletts_url'] = config.get('StyleTTS', 'tts_url')
        settings['gemini_api_key'] = config.get('Gemini', 'api_key')
        settings['gemini_model'] = config.get('Gemini', 'model')
        settings['ollama_model'] = config.get('Ollama', 'model')
        settings['ollama_vision_model'] = config.get('Ollama', 'vision_model', fallback='')
        settings['ollama_embedding_model'] = config.get('Ollama', 'embedding_model', fallback='')
        settings['ollama_api_url'] = config.get('Ollama', 'api_url')
        settings['osc_enabled'] = config.getboolean('OSC', 'enabled', fallback=False)
        settings['osc_ip'] = config.get('OSC', 'ip')
        settings['osc_port'] = config.getint('OSC', 'port')
        settings['osc_address'] = config.get('OSC', 'address')
        raw_osc_verbs = config.get('OSC', 'trigger_verbs', fallback='')
        settings['osc_trigger_verbs'] = [verb.strip().lower() for verb in raw_osc_verbs.split(',') if verb.strip()]
        raw_rag_triggers = config.get('RAG', 'rag_trigger_words', fallback='')
        settings['rag_trigger_words'] = [trigger.strip().lower() for trigger in raw_rag_triggers.split(',') if trigger.strip()]
    except Exception as e:
        sys.exit(f"FATAL ERROR: A setting is missing or invalid in '{config_file}'. Details: {e}")
    return settings
# ------------------------------------------------------------------------------


# --- 2. INITIALIZATION ---
# ------------------------------------------------------------------------------
config = load_config()
app = Flask(__name__)
CORS(app)
gemini_model = None

VISION_HISTORY = deque(maxlen=5)
CURRENT_LOCATION = "the stream room"

try:
    chroma_client = chromadb.PersistentClient(path="gem_memory_db")
    chat_collection = chroma_client.get_or_create_collection(name="chat_history")
    image_collection = chroma_client.get_or_create_collection(name="images")
    print("MCP INFO: ChromaDB vector database is ready.")
except Exception as e:
    sys.exit(f"MCP FATAL ERROR: Could not initialize ChromaDB. Details: {e}")

def verify_ollama_models():
    """Checks if the configured Ollama models are actually available on the server."""
    if "ollama" not in config['llm_choice']: return
    print("MCP INFO: Verifying that required Ollama models are available...")
    try:
        tags_url = config['ollama_api_url'].replace('/api/chat', '/api/tags')
        response = requests.get(tags_url, timeout=10)
        response.raise_for_status()
        installed_models = {model['name'] for model in response.json().get('models', [])}
    except Exception as e:
        print(f"MCP WARNING: Could not get model list from Ollama. Skipping verification. Details: {e}")
        return
    required_models = set()
    if config['llm_choice'] == 'ollama': required_models.add(config.get('ollama_model'))
    elif config['llm_choice'] == 'ollama_vision': required_models.add(config.get('ollama_vision_model'))
    required_models.add(config.get('ollama_embedding_model'))
    required_models.discard(None); required_models.discard('')
    all_models_found = True
    for model_name in required_models:
        if model_name not in installed_models:
            print(f"\nFATAL ERROR: The required Ollama model '{model_name}' is not available.")
            print("Please pull the model with 'ollama pull <model_name>' or correct the name in mcp_settings.ini.\n")
            all_models_found = False
    if not all_models_found: sys.exit(1)
    print("MCP INFO: All required Ollama models were found.")

if config['llm_choice'] == "gemini":
    print("MCP INFO: Initializing Gemini...")
    try:
        if not config['gemini_api_key'] or config['gemini_api_key'] == 'YOUR_GEMINI_API_KEY_HERE':
            sys.exit("FATAL ERROR: llm_choice is 'gemini' but api_key is not set.")
        genai.configure(api_key=config['gemini_api_key'])
        gemini_model = genai.GenerativeModel(config['gemini_model'])
        print(f"MCP INFO: Gemini model '{config['gemini_model']}' loaded.")
    except Exception as e:
        sys.exit(f"MCP FATAL ERROR: Failed to configure Gemini API. Details: {e}")
elif config['llm_choice'] in ["ollama", "ollama_vision"]:
    print("MCP INFO: Verifying Ollama connection...")
    try:
        requests.get(config['ollama_api_url'].rsplit('/', 1)[0])
        print(f"MCP INFO: Ollama connection successful.")
        verify_ollama_models()
    except requests.exceptions.ConnectionError:
        sys.exit("MCP FATAL ERROR: Could not connect to Ollama. Is it running?")

osc_client = None
if config['osc_enabled']:
    try:
        osc_client = udp_client.SimpleUDPClient(config['osc_ip'], config['osc_port'])
        print(f"MCP INFO: OSC client configured to send to {config['osc_ip']}:{config['osc_port']}")
    except Exception as e:
        print(f"MCP WARNING: Could not create OSC client. Details: {e}")
# ------------------------------------------------------------------------------


# --- 3. CORE HELPER FUNCTIONS ---
# ------------------------------------------------------------------------------
def get_embedding(text: str = None, image_base64: str = None) -> list[float]:
    """Gets a vector embedding from Ollama using a dedicated multimodal embedding model."""
    if not text and not image_base64: return None
    model_to_use = config.get('ollama_embedding_model')
    if not model_to_use:
        print("MCP ERROR: No embedding model configured in mcp_settings.ini.")
        return None
    payload = {"model": model_to_use, "prompt": text if text else " "}
    if image_base64: payload["images"] = [image_base64]
    try:
        embedding_url = config['ollama_api_url'].replace('/api/chat', '/api/embeddings')
        response = requests.post(embedding_url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json().get('embedding')
    except Exception as e:
        print(f"MCP ERROR: Could not get embedding from Ollama. Details: {e}")
        return None

def add_chat_to_memory(speaker: str, text: str):
    """Creates an embedding and stores it in the ChromaDB collection."""
    vector = get_embedding(text=text)
    if vector:
        try:
            doc_id = datetime.datetime.now().isoformat()
            chat_collection.add(
                ids=[doc_id],
                embeddings=[vector],
                metadatas=[{"speaker": speaker, "text_content": text, "timestamp": doc_id}]
            )
            print(f"MCP MEMORY: Added chat from '{speaker}' to ChromaDB.")
        except Exception as e:
            print(f"MCP ERROR: Failed to add chat to ChromaDB. Details: {e}")

def add_image_to_memory(image_identifier: str, image_base64: str):
    """Creates an embedding and stores it in the ChromaDB collection."""
    vector = get_embedding(image_base64=image_base64)
    if vector:
        try:
            image_collection.add(
                ids=[image_identifier],
                embeddings=[vector],
                metadatas=[{"timestamp": image_identifier}]
            )
            print(f"MCP MEMORY: Added image '{image_identifier}' to ChromaDB.")
        except Exception as e:
            print(f"MCP ERROR: Failed to add image to ChromaDB. Details: {e}")

def ask_llm(user_content: str, image_data_base64: str = None) -> str:
    """Sends the user's content and a system prompt to the selected LLM."""
    print(f"MCP INFO: Sending prompt to {config['llm_choice'].upper()}...")
    try:
        response = None
        system_prompt = config.get('system_prompt', '')
        if config['llm_choice'] in ['ollama_vision', 'ollama']:
            model = config['ollama_vision_model'] if config['llm_choice'] == 'ollama_vision' else config['ollama_model']
            user_message = {"role": "user", "content": user_content}
            if image_data_base64:
                user_message["images"] = [image_data_base64]
            messages = [{"role": "system", "content": system_prompt}, user_message]
            payload = {"model": model, "messages": messages, "stream": False}
            response = requests.post(config['ollama_api_url'], json=payload, timeout=60)
        elif config['llm_choice'] == 'gemini':
            final_gemini_prompt = f"{system_prompt}\n\n---\n\n{user_content}"
            gemini_response = gemini_model.generate_content(final_gemini_prompt)
            return gemini_response.text.strip()
        if response:
            response.raise_for_status()
            return response.json().get('message', {}).get('content', '').strip()
        return "Error: LLM choice not recognized."
    except Exception as e:
        print(f"MCP ERROR: An exception occurred in ask_llm. Details: {e}")
        return "Sorry, I encountered an error while trying to think."

def retrieve_from_rag(user_query: str) -> str:
    """Performs a RAG search and returns a formatted context string. DOES NOT CALL LLM."""
    print(f"MCP INFO: RAG retrieval triggered for query: '{user_query}'")
    query_vector = get_embedding(text=user_query)
    if not query_vector: return ""
    context_str = "CONTEXT FROM LONG-TERM MEMORY:\n"
    found_context = False
    try:
        chat_results = chat_collection.query(query_embeddings=[query_vector], n_results=3)
        if chat_results and chat_results['ids'][0]:
            context_str += "[Relevant Chat History]\n"
            for data in chat_results['metadatas'][0]:
                context_str += f"- {data['speaker']} said: \"{data['text_content']}\"\n"
            found_context = True
        image_results = image_collection.query(query_embeddings=[query_vector], n_results=1)
        if image_results and image_results['ids'][0]:
            context_str += "\n[Relevant Image]\n"
            context_str += f"- An image was found, identified as: '{image_results['ids'][0][0]}'\n"
            found_context = True
    except Exception as e:
        print(f"MCP ERROR: Failed during RAG search with ChromaDB. Details: {e}")
        return ""
    return context_str if found_context else ""

def send_over_osc(command_text: str):
    """Sends a command directly over OSC."""
    if not config['osc_enabled'] or not osc_client: return
    try:
        builder = osc_message_builder.OscMessageBuilder(address=config['osc_address'])
        builder.add_arg(command_text, builder.ARG_TYPE_STRING); builder.add_arg(True, builder.ARG_TYPE_TRUE)
        osc_client.send(builder.build())
        print(f"MCP INFO: Sent OSC command to {config['osc_address']} -> '{command_text}'")
    except Exception as e: print(f"MCP ERROR: Failed to send OSC message. Details: {e}")

def get_image_from_vision_service() -> str:
    """Gets a Base64 encoded image from the vision service."""
    url = config.get('vision_service_get_image_url')
    if not url:
        print("MCP ERROR: The 'vision_service_get_image_url' is not set in mcp_settings.ini.")
        return None
    print(f"MCP CORE: Requesting a fresh image from URL: {url}...")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        response_json = response.json()
        if "image_base64" not in response_json:
            print("MCP ERROR: Response from vision.py was valid JSON but missing 'image_base64' key.")
            return None
        return response_json.get("image_base64")
    except Exception as e:
        print(f"MCP ERROR: An unexpected error occurred while getting the image: {e}")
        return None

def get_fresh_vision_context() -> str:
    """Gets a text description from the legacy vision service."""
    url = config.get('vision_service_scan_url')
    if not url: return "Error: Vision service URL not configured."
    print(f"MCP CORE: Requesting a fresh vision scan from {url}...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json().get("vision_context", "Error: Invalid response from vision service.")
    except Exception as e: return f"Error: Could not reach vision service. Is it running? Details: {e}"

def send_to_social_stream(text_to_send: str):
    """Broadcasts text to all configured Social Stream platforms."""
    if not config.get('social_stream_enabled', False): return
    if not text_to_send or text_to_send.startswith("ACTION_GOTO:"): return
    targets = config.get('social_stream_targets', [])
    session_id = config.get('social_stream_session_id')
    api_url = config.get('social_stream_api_url')
    if not all([targets, session_id, api_url]):
        print("MCP DEBUG: Did not send to Social Stream because required settings are missing.")
        return
    print(f"MCP INFO: Broadcasting to Social Stream targets: {targets}")
    for target in targets:
        url = f"{api_url}/{session_id}"
        payload = {"action": "sendChat", "value": text_to_send, "target": target}
        print(f"  -> Sending to '{target}'...")
        try:
            requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10).raise_for_status()
            print(f"  -> SUCCESS: Message accepted for '{target}'.")
        except Exception as e:
            print(f"  -> FAILED: Could not send to '{target}'. Details: {e}")

def send_to_tts(text_to_speak: str):
    """Sends text to the TTS server."""
    if not config.get('styletts_enabled', False): return
    if not text_to_speak or text_to_speak.startswith("ACTION_GOTO:"): return
    url = config.get('styletts_url')
    if not url: return
    clean_text = re.sub(r"[^a-zA-Z0-9\s.,?!'-:;]", '', text_to_speak)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    if not clean_text: return
    payload = {"chatmessage": clean_text}
    print(f"MCP INFO: Sending SANITIZED text to StyleTTS Server -> '{clean_text}'")
    try:
        requests.post(url, json=payload, timeout=15).raise_for_status()
        print("MCP INFO: StyleTTS server accepted the request.")
    except Exception as e: print(f"MCP ERROR: Could not send to StyleTTS server. Details: {e}")
# ------------------------------------------------------------------------------


# --- 4. UNIVERSAL PROCESSING FUNCTION ---
# ------------------------------------------------------------------------------
def process_task(source: str, user_text: str, vision_context: str = "") -> str:
    """The central logic hub with a clear separation of retrieval and generation."""
    global VISION_HISTORY, CURRENT_LOCATION
    
    # 1. Case-Insensitive, Strict Wake Word Gatekeeper
    wake_word_detected, clean_user_text = False, ""
    for word in config['wake_words']:
        if not word: continue
        pattern = re.compile(r"^(ok |so |well |hey |okay, |so, |well, |hey, )?" + re.escape(word) + r"\b", re.IGNORECASE)
        match = pattern.search(user_text)
        if match:
            wake_word_detected, start_of_clean_text = True, match.end()
            clean_user_text = user_text[start_of_clean_text:].strip()
            if clean_user_text and clean_user_text[0] in [',', '.', ':', ';']:
                clean_user_text = clean_user_text[1:].strip()
            break
    if not wake_word_detected:
        print(f"MCP: No valid wake word pattern found in '{user_text}'. Ignoring.")
        return ""
    print(f"MCP: Wake word confirmed! Processing: '{clean_user_text}'")
    add_chat_to_memory("User", clean_user_text)

    # 2. Check for special commands and route accordingly
    is_rag_request = any(clean_user_text.lower().startswith(trigger) for trigger in config['rag_trigger_words'])
    is_osc_request = config['osc_enabled'] and any(clean_user_text.lower().startswith(verb) for verb in config['osc_trigger_verbs'])
    is_vision_request = any(trigger in clean_user_text.lower() for trigger in config['vision_trigger_words'])
    
    final_response = ""

    if is_osc_request:
        # --- OSC WORKFLOW (TRUE BYPASS) ---
        verb_found = next((verb for verb in config['osc_trigger_verbs'] if clean_user_text.lower().startswith(verb)), "")
        destination = clean_user_text[len(verb_found):].strip()
        if not destination:
            final_response = "Where do you want me to go?"
        elif destination.lower() == CURRENT_LOCATION.lower():
            final_response = f"I'm already at {destination}."
        else:
            send_over_osc(clean_user_text); CURRENT_LOCATION = destination
            final_response = f"Okay, I'm heading to {destination} now."
    elif is_vision_request:
        # --- VISION WORKFLOW (SPECIAL PROMPT) ---
        if config['llm_choice'] == 'ollama_vision':
            image_data = get_image_from_vision_service()
            if image_data:
                vision_prompt = f"In one or two short sentences, describe the main subject of the attached image. The user's original question was: '{clean_user_text}'"
                final_response = ask_llm(vision_prompt, image_data_base64=image_data)
                image_id = f"image_seen_at_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                add_image_to_memory(image_id, image_data)
                VISION_HISTORY.appendleft(f"User asked about an image ({image_id}), you saw: {final_response}")
            else: final_response = "Sorry, I couldn't get an image from the camera."
        else: # Pipelined legacy mode
            description = get_fresh_vision_context()
            VISION_HISTORY.appendleft(description); final_response = description
    else:
        # --- RAG AND STANDARD TEXT WORKFLOW ---
        # Start by gathering all available context.
        long_term_memory = ""
        if is_rag_request:
            long_term_memory = retrieve_from_rag(clean_user_text)
        
        location_context = f"Your current location is: {CURRENT_LOCATION}."
        history_context = ""
        if VISION_HISTORY:
            history_items = "\n".join(f"- {item}" for item in VISION_HISTORY)
            history_context = f"Short term memory of recent events:\n{history_items}"
        
        # Assemble the final prompt for the LLM
        prompt_for_llm = f"{long_term_memory}\n{location_context}\n{history_context}\n\n---\nBased on all available context, answer the user's question:\n\"{clean_user_text}\""
        final_response = ask_llm(prompt_for_llm)

    # Store AI's final response and return
    add_chat_to_memory("Gem", final_response)
    return final_response
# ------------------------------------------------------------------------------


# --- 5. API ENDPOINTS ---
# ------------------------------------------------------------------------------
@app.route('/', methods=['GET'])
def index(): return "Hello from the UNIFIED Master Control Program!"

@app.route('/chat', methods=['POST', 'PUT'])
def handle_chat_request():
    data = request.json
    chat_message = data.get('chatmessage', '')
    print(f"\nMCP: Received from [Chat]: '{chat_message}'")
    final_response = process_task(source='chat', user_text=chat_message)
    if final_response:
        send_to_tts(final_response)
        send_to_social_stream(final_response)
    return jsonify({"status": "ok"})

@app.route('/vision', methods=['POST'])
def handle_vision_request():
    data = request.json
    user_text = data.get('text', ''); vision_context = data.get('vision_context', '')
    print(f"\nMCP: Received from [Vision]: '{user_text}'")
    final_response = process_task(source='vision', user_text=user_text, vision_context=vision_context)
    if final_response:
        send_to_tts(final_response)
        send_to_social_stream(final_response)
    return jsonify({'response': final_response})
    
@app.route('/audio', methods=['POST'])
def handle_audio_request():
    data = request.json
    user_text = data.get('text', '')
    print(f"\nMCP: Received from [Audio]: '{user_text}'")
    final_response = process_task(source='audio', user_text=user_text)
    if final_response:
        send_to_tts(final_response)
        send_to_social_stream(final_response)
    return jsonify({'response': final_response})

@app.route('/update_vision', methods=['POST'])
def update_vision_context():
    global VISION_HISTORY
    data = request.json
    new_context = data.get('vision_context')
    if new_context:
        print(f"\nMCP MEMORY: Visual history has been UPDATED -> '{new_context[:70]}...'")
        VISION_HISTORY.appendleft(new_context)
    return jsonify({"status": "vision context updated"})
# ------------------------------------------------------------------------------


# --- 6. MAIN EXECUTION BLOCK ---
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    print("\n" + "="*70)
    print("--- Starting UNIFIED Master Control Program (MCP) ---")
    print(f"--- LLM Mode: {config['llm_choice'].upper()} ---")
    if config['osc_enabled']: print(f"--- OSC sending ENABLED to {config['osc_ip']}:{config['osc_port']} ---")
    else: print("--- OSC sending is DISABLED ---")
    print(f"--- API Server listening on http://{config['host']}:{config['port']} ---")
    print("="*70 + "\n")
    app.run(host=config['host'], port=config['port'], debug=True)
# ------------------------------------------------------------------------------