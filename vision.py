# ===========================================================================
#              DUAL-MODE Vision Service & Client for MCP
# ===========================================================================
# This script can operate in two modes based on the 'enable_local_vlm' setting:
#
# 1. VLM Mode (enable_local_vlm = true):
#    - Loads a local VLM (SmolVLM) to generate text descriptions of scenes.
#    - Provides the `/scan` endpoint for the pipelined MCP modes.
#    - Supports the interactive user input loop.
#
# 2. Camera Service Mode (enable_local_vlm = false):
#    - Does NOT load the VLM, saving significant memory/GPU resources.
#    - Acts as a simple, fast camera server.
#    - Provides the `/get_image` endpoint, which returns raw, Base64-encoded
#      image data for the unified multimodal MCP mode.
# ===========================================================================

import requests
import configparser
import sys
import os
import threading
import time
from PIL import Image
import torch
from transformers import AutoModelForVision2Seq, AutoProcessor
import cv2
from flask import Flask, jsonify
import base64
import io

# --- 1. CONFIGURATION & GLOBAL VARIABLES ---
config = {}
SMOL_VLM_MODEL_ID = "HuggingFaceTB/SmolVLM-500M-Instruct"
device = "cuda" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.bfloat16 if device == "cuda" else torch.float32

# VLM components are now optional and loaded conditionally
processor = None
smol_vlm_model = None

camera_stream = None
vision_app = Flask("VisionService")
# ------------------------------------------------------------------------------


# --- 2. CORE FUNCTIONS ---
def load_config():
    """Loads all settings from vision_settings.ini, including the new mode switch."""
    global config
    parser = configparser.ConfigParser()
    config_file = 'vision_settings.ini'
    if not os.path.exists(config_file): sys.exit(f"FATAL: Config '{config_file}' not found.")
    parser.read(config_file)
    settings = {}
    try:
        # NEW: Mode switch to decide if we load the local VLM
        settings['enable_local_vlm'] = parser.getboolean('Vision', 'enable_local_vlm', fallback=False)

        settings['camera_index'] = parser.getint('Vision', 'camera_index')
        raw_triggers = parser.get('Vision', 'vision_trigger_words', fallback='')
        settings['vision_trigger_words'] = [word.strip().lower() for word in raw_triggers.split(',') if word.strip()]
        settings['mcp_url'] = parser.get('MCP', 'mcp_url')
        settings['mcp_update_vision_url'] = parser.get('MCP', 'mcp_update_vision_url')
    except Exception as e: sys.exit(f"FATAL: Setting missing or invalid in '{config_file}'. Details: {e}")
    config = settings

def initialize_models():
    """Loads the VLM. This function is now called conditionally."""
    global processor, smol_vlm_model
    print(f"VISION INFO: Loading VLM: {SMOL_VLM_MODEL_ID} on '{device}'. (This may take a moment)...")
    try:
        processor = AutoProcessor.from_pretrained(SMOL_VLM_MODEL_ID, trust_remote_code=True)
        smol_vlm_model = AutoModelForVision2Seq.from_pretrained(SMOL_VLM_MODEL_ID, torch_dtype=torch_dtype, trust_remote_code=True, low_cpu_mem_usage=True).to(device)
        print("VISION INFO: VLM loaded successfully.")
    except Exception as e: sys.exit(f"FATAL: Could not load VLM. Details: {e}")

class CameraStream:
    """A dedicated thread to continuously read frames from the camera to prevent stale frames."""
    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened(): raise IOError(f"Cannot open camera at index {camera_index}")
        self.frame = None
        self.lock = threading.Lock()
        self.stopped = False
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            if ret:
                with self.lock: self.frame = frame

    def get_current_frame(self):
        with self.lock:
            if self.frame is None: return None
            return Image.fromarray(cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB))

    def release(self):
        self.stopped = True
        if self.thread.is_alive(): self.thread.join()
        self.cap.release()

def encode_image_to_base64(image: Image.Image) -> str:
    """Encodes a PIL Image into a Base64 string for JSON transport."""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# --- LEGACY VLM FUNCTIONS (Only used if enable_local_vlm is true) ---
def ask_smol_vlm(image: Image.Image, prompt_text: str) -> str:
    if not all([processor, smol_vlm_model]): return "Error: Local VLM not initialized."
    if image is None: return "Error: No image provided."
    messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": prompt_text}]}]
    prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
    inputs = processor(text=prompt, images=[image], return_tensors="pt").to(device, torch_dtype)
    try:
        output = smol_vlm_model.generate(**inputs, max_new_tokens=200, do_sample=False)
        generated_text = processor.batch_decode(output, skip_special_tokens=True)[0]
        separator = "Assistant:"
        if separator in generated_text:
            return generated_text.split(separator)[-1].strip()
        return generated_text.strip()
    except Exception as e: return f"Error: VLM inference failed. Details: {e}"

def send_to_mcp(user_text: str, vision_description: str) -> str:
    payload = {"source": "vision", "text": user_text, "vision_context": vision_description}
    try:
        response = requests.post(config['mcp_url'], json=payload)
        response.raise_for_status()
        return response.json().get('response', 'Error: Invalid response from MCP.')
    except requests.exceptions.RequestException as e: return f"MCP CONNECTION ERROR: {e}"
# ------------------------------------------------------------------------------


# --- 3. VISION SERVICE API ---
@vision_app.route('/scan', methods=['GET'])
def trigger_scan():
    """[LEGACY] Endpoint for pipelined mode. Returns a text description of the scene."""
    if not config.get('enable_local_vlm', False):
        return jsonify({"error": "Local VLM is not enabled in vision_settings.ini"}), 503
    
    global camera_stream
    if camera_stream is None: return jsonify({"error": "Camera stream not initialized"}), 500
    current_frame = camera_stream.get_current_frame()
    if current_frame:
        prompt = "Describe the main subject of the image in one short sentence."
        description = ask_smol_vlm(current_frame, prompt)
        return jsonify({"vision_context": description})
    else:
        return jsonify({"error": "Could not capture frame"}), 500

@vision_app.route('/get_image', methods=['GET'])
def get_image():
    """[NEW] Endpoint for unified multimodal mode. Returns a Base64-encoded image."""
    global camera_stream
    if camera_stream is None: return jsonify({"error": "Camera stream not initialized"}), 500
    current_frame = camera_stream.get_current_frame()
    if current_frame:
        base64_image = encode_image_to_base64(current_frame)
        return jsonify({"image_base64": base64_image})
    else:
        return jsonify({"error": "Could not capture frame"}), 500

def run_vision_server():
    host = "127.0.0.1"; port = 5001
    print(f"--- Vision Service API listening on http://{host}:{port} ---")
    vision_app.run(host=host, port=port, debug=False)
# ------------------------------------------------------------------------------


# --- 4. USER INPUT LOOP (LEGACY) ---
def user_input_loop():
    """Handles interactive commands. Only fully functional if local VLM is enabled."""
    if not config.get('enable_local_vlm', False):
        print("\n--- Interactive Client Disabled ---")
        print("Set 'enable_local_vlm = true' in vision_settings.ini to use this feature.")
        return

    global camera_stream
    print("\n--- Vision Client is Running (Pipelined Mode) ---")
    print("Type 'quit' or press Ctrl+C to exit.\n")
    while True:
        try:
            user_input = input("Enter command > ").strip()
            if not user_input: continue
            if user_input.lower() == "quit": break
            
            print("\n>>> Analyzing New Frame <<<")
            current_frame = camera_stream.get_current_frame()
            if current_frame:
                prompt = "Describe the main subject of the image in one short sentence."
                description = ask_smol_vlm(current_frame, prompt)
                print(f"Smol-VLM Context Being Sent: '{description}'")
                final_response = send_to_mcp(user_input, description)
                print(f"\n>>> MCP Response: {final_response}\n")
            else:
                print("Error: Could not capture a frame from the camera.")

        except KeyboardInterrupt: break
        except Exception as e:
            print(f"\nAn error occurred in the input loop: {e}")
            break
    
    # When loop exits, perform cleanup
    print("\nVISION INFO: Shutting down...")
    if camera_stream: camera_stream.release()
    os._exit(0)
# ------------------------------------------------------------------------------


# --- 5. MAIN EXECUTION BLOCK ---
if __name__ == '__main__':
    load_config()

    if config['enable_local_vlm']:
        initialize_models()
    else:
        print("VISION INFO: Local VLM is disabled. Running in Camera Service mode.")

    try:
        camera_stream = CameraStream(camera_index=config['camera_index'])
        print(f"VISION INFO: Camera stream started on index {config['camera_index']}.")
    except IOError as e:
        sys.exit(f"VISION FATAL ERROR: {e}. Exiting.")

    time.sleep(2) # Give camera time to initialize

    # Start the Flask server in a separate thread
    server_thread = threading.Thread(target=run_vision_server, daemon=True)
    server_thread.start()

    # --- [THE FIX] ---
    # If the interactive loop is disabled, we need to keep the main script alive.
    # Otherwise, the script will exit and the daemon server thread will be killed.
    if config.get('enable_local_vlm', False):
        # If the VLM is enabled, run the interactive loop as the main process.
        user_input_loop()
    else:
        # If the VLM is disabled, just wait for a keyboard interrupt (Ctrl+C).
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nVISION INFO: Ctrl+C detected. Shutting down...")
    
    # Perform cleanup when the script is told to exit.
    if camera_stream:
        camera_stream.release()
    print("VISION INFO: Script has shut down.")
    os._exit(0)
# ------------------------------------------------------------------------------