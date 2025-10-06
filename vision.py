# ===========================================================================
#                      Vision Service & Client for MCP
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

# --- 1. CONFIGURATION & GLOBAL VARIABLES ---
config = {}
SMOL_VLM_MODEL_ID = "HuggingFaceTB/SmolVLM-500M-Instruct"
device = "cuda" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.bfloat16 if device == "cuda" else torch.float32
processor = None
smol_vlm_model = None
camera_stream = None # Replaces video_processor
vision_app = Flask("VisionService")
# ------------------------------------------------------------------------------


# --- CAMERA STREAMING CLASS ---
class CameraStream:
    """
    A dedicated thread to continuously read frames from the camera.
    This prevents stale frames by ensuring the buffer is always being cleared.
    """
    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise IOError(f"Cannot open camera at index {camera_index}")
        
        self.frame = None
        self.lock = threading.Lock()
        self.stopped = False

        # Start the thread to read frames from the video stream
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        # This method runs in a separate thread
        while not self.stopped:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame

    def get_current_frame(self):
        # This method is called by the main application
        with self.lock:
            if self.frame is None:
                return None
            # Return a copy of the frame as a PIL Image
            return Image.fromarray(cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB))

    def release(self):
        self.stopped = True
        self.thread.join() # Wait for the thread to finish
        self.cap.release()
# ------------------------------------------------------------------------------


# --- 2. CORE FUNCTIONS (Mostly Unchanged) ---
def load_config():
    global config
    parser = configparser.ConfigParser()
    config_file = 'vision_settings.ini'
    if not os.path.exists(config_file): sys.exit(f"FATAL: Config '{config_file}' not found.")
    parser.read(config_file)
    settings = {}
    try:
        settings['camera_index'] = parser.getint('Vision', 'camera_index')
        raw_triggers = parser.get('Vision', 'vision_trigger_words', fallback='')
        settings['vision_trigger_words'] = [word.strip().lower() for word in raw_triggers.split(',') if word.strip()]
        settings['mcp_url'] = parser.get('MCP', 'mcp_url')
        settings['mcp_update_vision_url'] = parser.get('MCP', 'mcp_update_vision_url')
    except Exception as e: sys.exit(f"FATAL: Setting missing in '{config_file}'. Details: {e}")
    config = settings

def initialize_models():
    global processor, smol_vlm_model
    print(f"VISION INFO: Loading VLM: {SMOL_VLM_MODEL_ID} on '{device}'.")
    try:
        processor = AutoProcessor.from_pretrained(SMOL_VLM_MODEL_ID, trust_remote_code=True)
        smol_vlm_model = AutoModelForVision2Seq.from_pretrained(SMOL_VLM_MODEL_ID, torch_dtype=torch_dtype, trust_remote_code=True, low_cpu_mem_usage=True).to(device)
    except Exception as e: sys.exit(f"FATAL: Could not load VLM. Details: {e}")

def ask_smol_vlm(image: Image.Image, prompt_text: str) -> str:
    global processor, smol_vlm_model
    if image is None: return "Error: No image provided."
    messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": prompt_text}]}]
    prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
    inputs = processor(text=prompt, images=[image], return_tensors="pt").to(device, torch_dtype)
    try:
        output = smol_vlm_model.generate(**inputs, max_new_tokens=200, do_sample=False)
        generated_text = processor.batch_decode(output, skip_special_tokens=True)[0]

        # --- [NEW & IMPROVED CLEANING LOGIC] ---
        # The VLM is returning the full prompt context. We need to find the final
        # "Assistant:" marker and take only the text that comes after it.
        
        # Define the marker that separates the prompt from the actual answer
        separator = "Assistant:"
        
        if separator in generated_text:
            # Split the string by the separator and take the last part
            cleaned_text = generated_text.split(separator)[-1]
        else:
            # Fallback for other response formats
            cleaned_text = generated_text

        # Return the final, cleaned, and stripped text
        return cleaned_text.strip()
        # --- [END OF NEW LOGIC] ---

    except Exception as e: return f"Error: VLM inference failed. Details: {e}"

def send_to_mcp(user_text: str, vision_description: str) -> str:
    payload = {"source": "vision", "text": user_text, "vision_context": vision_description}
    try:
        response = requests.post(config['mcp_url'], json=payload)
        response.raise_for_status()
        return response.json().get('response', 'Error: Invalid response from MCP.')
    except requests.exceptions.RequestException as e: return f"MCP CONNECTION ERROR: Is MCP running? Details: {e}"

def update_mcp_vision_memory(vision_description: str):
    url = config.get('mcp_update_vision_url')
    if not url: return
    try:
        requests.post(url, json={"vision_context": vision_description}, timeout=2)
    except requests.exceptions.RequestException: pass
# ------------------------------------------------------------------------------


# --- 3. VISION SERVICE API ---
@vision_app.route('/scan', methods=['GET'])
def trigger_scan():
    global camera_stream
    if camera_stream is None: return jsonify({"error": "Camera stream not initialized"}), 500
    current_frame = camera_stream.get_current_frame()
    if current_frame:
        description = ask_smol_vlm(current_frame, "Describe the main subject of the image in one short sentence.")
        return jsonify({"vision_context": description})
    else:
        return jsonify({"error": "Could not capture frame"}), 500

def run_vision_server():
    host = "127.0.0.1"; port = 5001
    print(f"--- Vision Service API listening on http://{host}:{port} ---")
    vision_app.run(host=host, port=port, debug=False)
# ------------------------------------------------------------------------------


# --- 4. USER INPUT LOOP ---
def user_input_loop():
    global camera_stream
    last_vision_context = ""
    time.sleep(1) 
    
    print("\n--- Vision Client is Running (Robust Camera Logic) ---")
    print("Type 'quit' or press Ctrl+C to exit.\n")

    while True:
        try:
            user_input = input("Enter command > ").strip()
            if not user_input: continue
            if user_input.lower() == "quit":
                camera_stream.release()
                os._exit(0)

            lower_user_input = user_input.lower()
            needs_new_vision = any(trigger in lower_user_input for trigger in config['vision_trigger_words']) or not last_vision_context
            
            context_for_this_request = ""
            if needs_new_vision:
                print("\n>>> Analyzing New Frame <<<")
                current_frame = camera_stream.get_current_frame()
                if current_frame:
                    new_description = ask_smol_vlm(current_frame, "Describe the main subject of the image in one short sentence.")
                    context_for_this_request = new_description
                    last_vision_context = new_description
                    update_mcp_vision_memory(last_vision_context)
                else:
                    context_for_this_request = "Error: Could not capture frame."
                    last_vision_context = ""
            else:
                print("\n>>> Using Cached Vision Context <<<")
                context_for_this_request = last_vision_context
            
            print(f"Smol-VLM Context Being Sent: '{context_for_this_request}'")
            final_response = send_to_mcp(user_input, context_for_this_request)
            print(f"\n>>> MCP Response: {final_response}\n")

        except KeyboardInterrupt:
            print("\nVISION INFO: Ctrl+C detected. Shutting down...")
            camera_stream.release()
            os._exit(0)
        except Exception as e:
            print(f"\nAn error occurred in the input loop: {e}")
            camera_stream.release()
            os._exit(1)
# ------------------------------------------------------------------------------


# --- 5. MAIN EXECUTION BLOCK ---
if __name__ == '__main__':
    load_config()
    initialize_models()
    try:
        # Initialize our new robust camera stream
        camera_stream = CameraStream(camera_index=config['camera_index'])
    except IOError as e:
        sys.exit(f"VISION FATAL ERROR: {e}. Exiting.")

    # Give the camera a moment to start up and fill the first frame
    time.sleep(2)

    input_thread = threading.Thread(target=user_input_loop, daemon=True)
    input_thread.start()

    run_vision_server()