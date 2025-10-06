# ==============================================================================
#                           Master Control Program
# ==============================================================================


import requests
import json
import configparser
import sys
import os
import google.generativeai as genai
import re

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
        # --- [NEW] Load the system prompt ---
        settings['system_prompt'] = config.get('SystemPrompt', 'prompt', fallback='').strip()
        # --- [END NEW] ---

        settings['llm_choice'] = config.get('MCP', 'llm_choice')
        settings['host'] = config.get('MCP', 'host')
        settings['port'] = config.getint('MCP', 'port')
        settings['max_response_length'] = config.getint('Assistant', 'max_response_length', fallback=0)
        raw_wake_words = config.get('Assistant', 'wake_words', fallback='')
        settings['wake_words'] = [word.strip().lower() for word in raw_wake_words.split(',') if word.strip()]
        raw_command_verbs = config.get('Assistant', 'command_verbs', fallback='')
        settings['command_verbs'] = [verb.strip().lower() for verb in raw_command_verbs.split(',') if verb.strip()]
        settings['vision_service_scan_url'] = config.get('VisionService', 'scan_url')
        raw_triggers = config.get('VisionService', 'vision_trigger_words', fallback='')
        settings['vision_trigger_words'] = [word.strip().lower() for word in raw_triggers.split(',') if word.strip()]
        settings['social_stream_enabled'] = config.getboolean('SocialStream', 'enabled', fallback=False)
        settings['social_stream_session_id'] = config.get('SocialStream', 'session_id')
        settings['social_stream_target_platform'] = config.get('SocialStream', 'target_platform')
        settings['social_stream_api_url'] = config.get('SocialStream', 'api_url')
        settings['styletts_enabled'] = config.getboolean('StyleTTS', 'enabled', fallback=False)
        settings['styletts_url'] = config.get('StyleTTS', 'tts_url')
        settings['gemini_api_key'] = config.get('Gemini', 'api_key')
        settings['gemini_model'] = config.get('Gemini', 'model')
        settings['ollama_model'] = config.get('Ollama', 'model')
        settings['ollama_api_url'] = config.get('Ollama', 'api_url')
    except Exception as e:
        sys.exit(f"FATAL ERROR: Missing a setting in '{config_file}'. Details: {e}")
    return settings
# ------------------------------------------------------------------------------


# --- 2. INITIALIZATION ---
# ------------------------------------------------------------------------------
config = load_config()
app = Flask(__name__)
CORS(app)
gemini_model = None
LATEST_VISION_CONTEXT = "No visual context has been provided yet."

if config['llm_choice'] == "gemini":
    print("MCP INFO: Initializing Gemini...")
    try:
        if not config['gemini_api_key'] or config['gemini_api_key'] == 'YOUR_GEMINI_API_KEY_HERE':
            sys.exit("FATAL ERROR: llm_choice is 'gemini' but api_key is not set in 'mcp_settings.ini'.")
        genai.configure(api_key=config['gemini_api_key'])
        gemini_model = genai.GenerativeModel(config['gemini_model'])
        print(f"MCP INFO: Gemini model '{config['gemini_model']}' loaded.")
    except Exception as e:
        sys.exit(f"MCP FATAL ERROR: Failed to configure Gemini API. Details: {e}")
elif config['llm_choice'] == "ollama":
    print("MCP INFO: Verifying Ollama connection...")
    try:
        requests.get(config['ollama_api_url'].rsplit('/', 1)[0])
        print(f"MCP INFO: Ollama connection to '{config['ollama_model']}' successful.")
    except requests.exceptions.ConnectionError:
        sys.exit("MCP FATAL ERROR: Could not connect to Ollama. Is it running?")
# ------------------------------------------------------------------------------


# --- 3. CORE HELPER FUNCTIONS ---
# ------------------------------------------------------------------------------
def ask_llm(prompt: str) -> str:
    """Sends a prompt to the selected LLM, prefixed with the system prompt."""
    print(f"MCP INFO: Sending prompt to {config['llm_choice'].upper()}...")
    
    # Retrieve the system prompt from our global config
    system_prompt = config.get('system_prompt', '')

    if config['llm_choice'] == "gemini":
        try:
            # Combine system and user prompts for Gemini
            full_prompt = f"{system_prompt}\n\n---\n\n{prompt}"
            response = gemini_model.generate_content(full_prompt)
            return response.text.strip()
        except Exception as e: return f"Error from Gemini: {e}"

    elif config['llm_choice'] == "ollama":
        try:
            sanitized_model_name = config['ollama_model'].strip()
            # Create a message list with a system role for Ollama
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            payload = {"model": sanitized_model_name, "messages": messages, "stream": False}
            response = requests.post(config['ollama_api_url'], json=payload)
            response.raise_for_status()
            response_json = response.json()
            if 'message' in response_json and 'content' in response_json['message']:
                return response_json['message']['content'].strip()
            raise ValueError(f"Unexpected Ollama response: {response_json}")
        except Exception as e: return f"Error from Ollama: {e}"

    return "Error: LLM not configured."

def sanitize_for_tts(text: str) -> str:
    """Removes emojis and other non-standard characters for TTS engines."""
    if not text: return ""
    pattern = r"[^a-zA-Z0-9\s.,?!'-:;]"
    sanitized_text = re.sub(pattern, '', text)
    return re.sub(r'\s+', ' ', sanitized_text).strip()

def send_to_social_stream(text_to_send: str):
    """Sends the raw, emoji-friendly text to Social Stream Ninja."""
    if not config.get('social_stream_enabled', False): return
    if not text_to_send or text_to_send.startswith("ACTION_GOTO:"): return
    session_id = config.get('social_stream_session_id'); api_url = config.get('social_stream_api_url'); target_platform = config.get('social_stream_target_platform')
    if not session_id or not api_url or not target_platform: return
    url = f"{api_url}/{session_id}"
    payload = {"action": "sendChat", "value": text_to_send, "target": target_platform}
    print(f"MCP INFO: Sending to Social Stream Ninja -> '{text_to_send}'")
    try:
        requests.post(url, json=payload, headers={"Content-Type": "application/json"}).raise_for_status()
        print("MCP INFO: Social Stream Ninja accepted the message.")
    except Exception as e: print(f"MCP ERROR: Could not send to Social Stream Ninja. Details: {e}")

def send_to_tts(text_to_speak: str):
    """Sanitizes the text and then sends it to the StyleTTS2 server."""
    if not config.get('styletts_enabled', False): return
    if not text_to_speak or text_to_speak.startswith("ACTION_GOTO:"): return
    url = config.get('styletts_url')
    if not url: return
    clean_text = sanitize_for_tts(text_to_speak)
    if not clean_text: return
    payload = {"chatmessage": clean_text}
    print(f"MCP INFO: Sending SANITIZED text to StyleTTS Server -> '{clean_text}'")
    try:
        requests.post(url, json=payload, timeout=15).raise_for_status()
        print("MCP INFO: StyleTTS server accepted the request.")
    except Exception as e: print(f"MCP ERROR: Could not send to StyleTTS server. Details: {e}")

def get_fresh_vision_context() -> str:
    """Commands the vision service to perform a new scan and return the context."""
    url = config.get('vision_service_scan_url')
    if not url: return "Error: Vision service URL not configured."
    print(f"MCP CORE: Requesting a fresh vision scan from {url}...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        description = response.json().get("vision_context", "Error: Invalid response from vision service.")
        print(f"MCP CORE: Received fresh context: '{description[:70]}...'")
        return description
    except Exception as e: return f"Error: Could not reach vision service. Is it running? Details: {e}"
# ------------------------------------------------------------------------------


# --- 4. UNIVERSAL PROCESSING FUNCTION ---
# ------------------------------------------------------------------------------
def process_task(source: str, user_text: str, vision_context: str = "") -> str:
    """This is the central logic hub for all incoming tasks. (Final Logic)"""
    global LATEST_VISION_CONTEXT
    
    # 1. Wake Word Gatekeeper
    lower_user_text = user_text.lower().strip()
    wake_word_detected = False
    clean_user_text = user_text
    for word in config['wake_words']:
        if lower_user_text.startswith(word):
            wake_word_detected = True
            clean_user_text = user_text[len(word):].strip()
            break
    if not wake_word_detected:
        print("MCP: No wake word. Ignoring.")
        return ""

    print(f"MCP: Wake word confirmed! Processing: '{clean_user_text}'")

    # --- [FINAL CORRECTED BYPASS LOGIC] ---

    # 2a. Direct Vision Passthrough (from vision.py client)
    if source == 'vision':
        print("MCP INFO: Direct passthrough from vision client. Bypassing LLM.")
        LATEST_VISION_CONTEXT = vision_context
        return vision_context

    # 2b. On-Demand Vision Passthrough (from chat, audio, etc.)
    is_vision_request = any(trigger in clean_user_text.lower() for trigger in config['vision_trigger_words'])
    if is_vision_request:
        print("MCP: Vision trigger detected from a non-vision source. Performing scan and bypassing LLM.")
        description = get_fresh_vision_context()
        LATEST_VISION_CONTEXT = description # Update memory
        return description # Return the description directly as the final answer
    
    # --- [END OF BYPASS LOGIC] ---

    # 3. If we reach this point, it is a normal, non-visual question.
    print("MCP: Processing as a standard text-only request.")
    
    # We no longer need visual context for these prompts.
    augmented_prompt = f"Question: {clean_user_text}"
    
    # 4. Call LLM
    raw_llm_response = ask_llm(augmented_prompt)
    print(f"MCP: LLM Raw Response: '{raw_llm_response}'")

    # 5. Clean and Truncate Response
    cleaned_llm_response = raw_llm_response.replace("RESPONSE:", "").strip()
    max_len = config.get('max_response_length', 0)
    if max_len > 0 and len(cleaned_llm_response) > max_len:
        truncated_response = cleaned_llm_response[:max_len]
        last_space = truncated_response.rfind(' ')
        if last_space != -1:
            final_response = truncated_response[:last_space].strip() + "..."
        else:
            final_response = truncated_response + "..."
        print(f"MCP INFO: Final Truncated Response: '{final_response}'")
        return final_response
        
    return cleaned_llm_response
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
    user_text = data.get('text', '')
    vision_context = data.get('vision_context', '')
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
    global LATEST_VISION_CONTEXT
    data = request.json
    new_context = data.get('vision_context')
    if new_context:
        print(f"\nMCP MEMORY: Visual context has been UPDATED -> '{new_context[:70]}...'")
        LATEST_VISION_CONTEXT = new_context
    return jsonify({"status": "vision context updated"})
# ------------------------------------------------------------------------------


# --- 6. MAIN EXECUTION BLOCK ---
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    print("\n==============================================================================")
    print(f"--- Starting UNIFIED Master Control Program (MCP) ---")
    print(f"--- Using LLM: {config['llm_choice'].upper()} ---")
    print(f"--- API Server listening on http://{config['host']}:{config['port']} ---")
    print("==============================================================================\n")
    app.run(host=config['host'], port=config['port'], debug=True)
# ------------------------------------------------------------------------------