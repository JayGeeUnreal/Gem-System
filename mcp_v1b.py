# ==============================================================================
#                      Master Control Program (mcp.py)
#          - UNIFIED MULTIMODAL & PIPELINED ARCHITECTURE -
# ==============================================================================
# This script acts as the central brain for the AI system. It supports:
# - A unified multimodal mode ('ollama_vision') that sends images and text
#   directly to a capable model like Gemma.
# - The original pipelined modes ('ollama', 'gemini') that use a separate
#   vision service for text descriptions.
# - Location awareness, OSC command bypass, vision history, and more.
# ==============================================================================

import requests
import json
import configparser
import sys
import os
import google.generativeai as genai
import re
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
        # System Prompt
        settings['system_prompt'] = config.get('SystemPrompt', 'prompt', fallback='').strip()

        # MCP Core
        settings['llm_choice'] = config.get('MCP', 'llm_choice')
        settings['host'] = config.get('MCP', 'host')
        settings['port'] = config.getint('MCP', 'port')
        
        # Assistant Behavior
        settings['max_response_length'] = config.getint('Assistant', 'max_response_length', fallback=0)
        raw_wake_words = config.get('Assistant', 'wake_words', fallback='')
        settings['wake_words'] = [word.strip().lower() for word in raw_wake_words.split(',') if word.strip()]
        raw_command_verbs = config.get('Assistant', 'command_verbs', fallback='')
        settings['command_verbs'] = [verb.strip().lower() for verb in raw_command_verbs.split(',') if verb.strip()]
        
        # Vision Service
        settings['vision_service_scan_url'] = config.get('VisionService', 'scan_url')
        settings['vision_service_get_image_url'] = config.get('VisionService', 'vision_service_get_image_url', fallback='')
        raw_triggers = config.get('VisionService', 'vision_trigger_words', fallback='')
        settings['vision_trigger_words'] = [word.strip().lower() for word in raw_triggers.split(',') if word.strip()]

        # Social Stream (with multi-platform support)
        settings['social_stream_enabled'] = config.getboolean('SocialStream', 'enabled', fallback=False)
        settings['social_stream_session_id'] = config.get('SocialStream', 'session_id')
        raw_platforms = config.get('SocialStream', 'target_platforms', fallback='')
        settings['social_stream_targets'] = [p.strip() for p in raw_platforms.split(',') if p.strip()]
        settings['social_stream_api_url'] = config.get('SocialStream', 'api_url')
        
        # StyleTTS
        settings['styletts_enabled'] = config.getboolean('StyleTTS', 'enabled', fallback=False)
        settings['styletts_url'] = config.get('StyleTTS', 'tts_url')
        
        # LLM Models
        settings['gemini_api_key'] = config.get('Gemini', 'api_key')
        settings['gemini_model'] = config.get('Gemini', 'model')
        settings['ollama_model'] = config.get('Ollama', 'model')
        settings['ollama_vision_model'] = config.get('Ollama', 'vision_model', fallback='')
        settings['ollama_api_url'] = config.get('Ollama', 'api_url')

        # OSC Settings
        settings['osc_enabled'] = config.getboolean('OSC', 'enabled', fallback=False)
        settings['osc_ip'] = config.get('OSC', 'ip')
        settings['osc_port'] = config.getint('OSC', 'port')
        settings['osc_address'] = config.get('OSC', 'address')
        raw_osc_verbs = config.get('OSC', 'trigger_verbs', fallback='')
        settings['osc_trigger_verbs'] = [verb.strip().lower() for verb in raw_osc_verbs.split(',') if verb.strip()]

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
elif config['llm_choice'] in ["ollama", "ollama_vision"]:
    print("MCP INFO: Verifying Ollama connection...")
    try:
        requests.get(config['ollama_api_url'].rsplit('/', 1)[0])
        print(f"MCP INFO: Ollama connection to '{config['ollama_api_url']}' successful.")
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
def ask_llm(user_prompt: str, image_data_base64: str = None) -> str:
    """Sends a prompt (and optionally an image) to the selected LLM with robust debugging."""
    print(f"MCP INFO: Sending prompt to {config['llm_choice'].upper()}...")
    
    system_prompt = config.get('system_prompt', '')
    location_context = f"Your current location is: {CURRENT_LOCATION}.\n\n"
    history_context = ""
    if VISION_HISTORY:
        history_items = "\n".join(f"- {item}" for item in VISION_HISTORY)
        history_context = f"Here is a summary of the last few things you have seen (as text descriptions), from most to least recent:\n{history_items}\n\n"

    try:
        payload = {}
        if config['llm_choice'] == 'ollama_vision':
            enhanced_system_prompt = f"{system_prompt}\n\n{location_context}{history_context}"
            user_message = {"role": "user", "content": user_prompt}
            if image_data_base64:
                user_message["images"] = [image_data_base64]
            messages = [{"role": "system", "content": enhanced_system_prompt}, user_message]
            payload = {"model": config['ollama_vision_model'], "messages": messages, "stream": False}
        
        elif config['llm_choice'] == 'ollama':
            full_user_content = f"{location_context}{history_context}Based on that, answer the following:\n{user_prompt}"
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": full_user_content}]
            payload = {"model": config['ollama_model'], "messages": messages, "stream": False}
        
        elif config['llm_choice'] == 'gemini':
            full_user_content = f"{location_context}{history_context}Based on that, answer the following:\n{user_prompt}"
            full_prompt = f"{system_prompt}\n\n{full_user_content}"
            response = gemini_model.generate_content(full_prompt)
            return response.text.strip()

        # Request to Ollama
        response = requests.post(config['ollama_api_url'], json=payload, timeout=60)
        response.raise_for_status() 

        response_json = response.json()

        # --- [CRUCIAL DEBUG STEP] ---
        # Print the entire JSON response from Ollama so we can see its structure.
        print(f"MCP DEBUG: Raw JSON response from Ollama: {response_json}")
        # --- [END DEBUG STEP] ---

        # The current logic expects {"message": {"content": "..."}}
        # We will adjust this based on the debug output.
        return response_json.get('message', {}).get('content', '').strip()

    except requests.exceptions.HTTPError as http_err:
        print(f"MCP ERROR: HTTP Error occurred: {http_err}")
        print(f"MCP ERROR: Response Body from Ollama: {http_err.response.text}")
        return f"Sorry, there was an HTTP error from the AI model."
    except Exception as e:
        print(f"MCP ERROR: An exception occurred in ask_llm: {e}")
        return f"Sorry, an error occurred: {e}"

def get_image_from_vision_service() -> str:
    """Calls the simplified vision service to get a Base64 encoded image with better error handling."""
    url = config.get('vision_service_get_image_url')
    if not url:
        print("MCP ERROR: The 'vision_service_get_image_url' is not set in mcp_settings.ini.")
        return None
        
    print(f"MCP CORE: Requesting a fresh image from URL: {url}...")
    try:
        response = requests.get(url, timeout=15)
        # This will raise an error for 4xx or 5xx status codes
        response.raise_for_status()
        
        # Check if the key exists in the JSON
        response_json = response.json()
        if "image_base64" not in response_json:
            print("MCP ERROR: The response from vision.py was valid JSON, but the 'image_base64' key was missing.")
            return None
            
        return response_json.get("image_base64")

    except requests.exceptions.Timeout:
        print("MCP ERROR: The request to the vision service timed out. Is vision.py running and responsive?")
        return None
    except requests.exceptions.ConnectionError:
        print("MCP ERROR: Could not connect to the vision service. Is vision.py running on the correct host and port?")
        return None
    except requests.exceptions.JSONDecodeError:
        print("MCP ERROR: The vision service did not return valid JSON. The response was: " + response.text)
        return None
    except requests.exceptions.HTTPError as e:
        print(f"MCP ERROR: The vision service returned an HTTP error: {e._class.name_}")
        print(f"MCP ERROR: Full response from vision.py: {e.response.text}")
        return None
    except Exception as e:
        # A catch-all for any other unexpected errors
        print(f"MCP ERROR: An unexpected error occurred while getting the image: {e}")
        return None

def get_fresh_vision_context() -> str:
    """Commands the legacy vision service to perform a scan and return the text context."""
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

def send_over_osc(command_text: str):
    """Sends a command directly over OSC using a robust message builder."""
    if not config['osc_enabled'] or not osc_client:
        print("MCP WARNING: OSC is not enabled or client failed to initialize. Skipping send.")
        return
    try:
        builder = osc_message_builder.OscMessageBuilder(address=config['osc_address'])
        builder.add_arg(command_text, builder.ARG_TYPE_STRING)
        builder.add_arg(True, builder.ARG_TYPE_TRUE)
        msg = builder.build()
        osc_client.send(msg)
        print(f"MCP INFO: Sent ROBUST OSC message to {config['osc_address']} -> '{command_text}'")
    except Exception as e:
        print(f"MCP ERROR: Failed to send robust OSC message. Details: {e}")

def sanitize_for_tts(text: str) -> str:
    """Removes emojis and other non-standard characters for TTS engines."""
    if not text: return ""
    pattern = r"[^a-zA-Z0-9\s.,?!'-:;]"
    sanitized_text = re.sub(pattern, '', text)
    return re.sub(r'\s+', ' ', sanitized_text).strip()

def send_to_social_stream(text_to_send: str):
    """Broadcasts the text to ALL configured Social Stream Ninja platforms."""
    # First, check if the entire feature is enabled in the config file.
    if not config.get('social_stream_enabled', False):
        # This is a silent exit, but you could add a print statement if you want to know it's being skipped.
        # print("MCP DEBUG: Social Stream is disabled, skipping send.")
        return

    # Don't send empty messages or internal action commands.
    if not text_to_send or text_to_send.startswith("ACTION_GOTO:"):
        return

    # Retrieve the list of target platforms and other necessary settings from the config.
    targets = config.get('social_stream_targets', [])
    session_id = config.get('social_stream_session_id')
    api_url = config.get('social_stream_api_url')
    
    # Check if all the required settings are present and not empty.
    if not all([targets, session_id, api_url]):
        print("MCP DEBUG: Did not send to Social Stream because one or more required settings (target_platforms, session_id, api_url) are missing or empty in mcp_settings.ini.")
        return

    # --- This is the main broadcasting loop ---
    print(f"MCP INFO: Broadcasting to Social Stream targets: {targets}")
    
    # Loop through each target platform from your settings file.
    for target in targets:
        # Construct the full URL and the payload for the current target.
        url = f"{api_url}/{session_id}"
        payload = {"action": "sendChat", "value": text_to_send, "target": target}
        
        print(f"  -> Sending to '{target}'...")
        
        try:
            # The error handling is INSIDE the loop.
            # This makes the function robust: if one platform fails (e.g., Twitch is offline),
            # it will log the error and continue trying the other configured platforms.
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
            response.raise_for_status()
            print(f"  -> SUCCESS: Message accepted for '{target}'.")
        except Exception as e:
            print(f"  -> FAILED: Could not send to '{target}'. Details: {e}")
# ------------------------------------------------------------------------------


# --- 4. UNIVERSAL PROCESSING FUNCTION ---
# ------------------------------------------------------------------------------
def process_task(source: str, user_text: str, vision_context: str = "") -> str:
    """This is the central logic hub with improved, more flexible wake word detection."""
    global VISION_HISTORY, CURRENT_LOCATION
    
    # --- [NEW] 1. FLEXIBLE WAKE WORD GATEKEEPER ---
    lower_user_text = user_text.lower().strip()
    wake_word_detected = False
    clean_user_text = ""
    
    for word in config['wake_words']:
        # Find the position of the wake word in the sentence
        wake_word_pos = lower_user_text.find(word)
        
        # Check if the wake word was found near the beginning of the sentence
        # (e.g., within the first 15 characters, to avoid accidental triggers in long sentences)
        if 0 <= wake_word_pos < 15:
            wake_word_detected = True
            # The clean text is everything AFTER the wake word
            start_of_clean_text = wake_word_pos + len(word)
            clean_user_text = user_text[start_of_clean_text:].strip()
            # If the character after the wake word is a common punctuation mark, strip it.
            if clean_user_text and clean_user_text[0] in [',', '.', ':', ';']:
                clean_user_text = clean_user_text[1:].strip()
            break # Stop after finding the first valid wake word
            
    if not wake_word_detected:
        print(f"MCP: No wake word found near the start of '{user_text}'. Ignoring.")
        return ""
    # --- [END NEW] ---

    print(f"MCP: Wake word confirmed! Processing: '{clean_user_text}'")

    # 2. Location-Aware OSC Command Bypass
    if config['osc_enabled']:
        for verb in config['osc_trigger_verbs']:
            if clean_user_text.lower().startswith(verb):
                destination = clean_user_text[len(verb):].strip()
                if not destination: return "Where do you want me to go?"
                print(f"MCP INFO: OSC movement command detected. Destination: '{destination}'")
                if destination.lower() == CURRENT_LOCATION.lower():
                    print(f"MCP INFO: Already at '{destination}'. No OSC command sent.")
                    return f"I'm already at {destination}."
                else:
                    print(f"MCP INFO: Moving to '{destination}'. Sending OSC command.")
                    send_over_osc(clean_user_text)
                    CURRENT_LOCATION = destination
                    return f"Okay, I'm heading to {destination} now."

    # 3. ARCHITECTURE ROUTER
    is_vision_capable_mode = config['llm_choice'] == 'ollama_vision'
    is_vision_request = any(trigger in clean_user_text.lower() for trigger in config['vision_trigger_words'])

    final_response = ""
    if is_vision_capable_mode:
        print("MCP INFO: Operating in UNIFIED multimodal mode.")
        if is_vision_request:
            image_data = get_image_from_vision_service()
            if image_data:
                final_response = ask_llm(clean_user_text, image_data_base64=image_data)
                VISION_HISTORY.appendleft(f"The user asked '{clean_user_text}' about an image and you saw: {final_response}")
            else:
                final_response = "Sorry, I tried to look but couldn't get an image from the camera."
        else:
            final_response = ask_llm(clean_user_text)
    else:
        print("MCP INFO: Operating in PIPELINED text-only mode.")
        if source == 'vision':
            VISION_HISTORY.appendleft(vision_context)
            final_response = vision_context
        elif is_vision_request:
            description = get_fresh_vision_context()
            VISION_HISTORY.appendleft(description)
            final_response = description
        else:
            final_response = ask_llm(clean_user_text)

    # 4. Clean and Truncate Final Response
    cleaned_llm_response = final_response.replace("RESPONSE:", "").strip()
    max_len = config.get('max_response_length', 0)
    if max_len > 0 and len(cleaned_llm_response) > max_len:
        truncated_response = cleaned_llm_response[:max_len]
        last_space = truncated_response.rfind(' ')
        if last_space != -1:
            return truncated_response[:last_space].strip() + "..."
        else:
            return truncated_response + "..."
    return cleaned_llm_response


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
    print("\n==============================================================================")
    print(f"--- Starting UNIFIED Master Control Program (MCP) ---")
    print(f"--- Using LLM Mode: {config['llm_choice'].upper()} ---")
    if config['osc_enabled']:
        print(f"--- OSC sending is ENABLED to {config['osc_ip']}:{config['osc_port']} ---")
    else:
        print(f"--- OSC sending is DISABLED ---")
    print(f"--- API Server listening on http://{config['host']}:{config['port']} ---")
    print("==============================================================================\n")
    app.run(host=config['host'], port=config['port'], debug=True)
# ------------------------------------------------------------------------------