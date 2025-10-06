# ==============================================================================
#                      Audio Client for MCP
# ==============================================================================
# This script acts as the "ears" of the system. Its sole purpose is to listen
# via the microphone, use a local Whisper model to transcribe speech, and send
# the resulting text to the MCP for filtering and reasoning.
# ==============================================================================

import collections
import queue
import sys
import wave
import os
import requests
import configparser

import numpy as np
import sounddevice as sd
import webrtcvad
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from scipy.io.wavfile import read as read_wav

# --- Configuration (static values) ---
VAD_AGGRESSIVENESS = 3
SAMPLE_RATE = 16000
FRAME_DURATION_MS = 20
FRAMES_PER_BUFFER = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)
SILENCE_THRESHOLD_S = 1.5
PRE_BUFFER_S = 0.5
WAV_FILE_NAME = "temp_audio_chunk.wav" # Renamed for clarity

# --- Global State ---
audio_queue = queue.Queue()
is_recording = False
pre_buffer_frames = collections.deque(maxlen=int(PRE_BUFFER_S * SAMPLE_RATE / FRAMES_PER_BUFFER))
recorded_frames = []
silent_frames_count = 0

# --- CORE FUNCTIONS ---

def load_config():
    """Loads settings from the simplified listen.ini file."""
    config = configparser.ConfigParser()
    config_file = 'listen.ini'
    if not os.path.exists(config_file):
        sys.exit(f"FATAL ERROR: Configuration file '{config_file}' not found.")
    config.read(config_file)
    settings = {}
    settings['mcp_url'] = config.get('MCP', 'mcp_url')
    return settings

def send_to_mcp(transcribed_text: str, mcp_url: str):
    """Packages the transcribed text and sends it to the MCP."""
    print(f"AUDIO INFO: Sending to MCP -> '{transcribed_text}'")
    payload = {
        "source": "microphone",
        "text": transcribed_text,
        "vision_context": "" # Audio client has no vision context
    }
    try:
        response = requests.post(mcp_url, json=payload, timeout=5)
        response.raise_for_status()
        print("AUDIO INFO: MCP received the task.")
    except requests.exceptions.RequestException as e:
        print(f"MCP CONNECTION ERROR: Could not connect. Is MCP running? Details: {e}")

def select_audio_device():
    # ... (This function is unchanged) ...
    print("Available audio input devices:")
    devices = sd.query_devices()
    input_devices = [d for d in devices if d['max_input_channels'] > 0]
    if not input_devices: sys.exit("Error: No audio input devices found.")
    default_idx = sd.default.device[0]
    for i, device in enumerate(input_devices):
        print(f"  {device['index']}: {device['name']} {'(default)' if device['index'] == default_idx else ''}")
    while True:
        choice = input(f"Enter device index (or press Enter for default): ")
        if choice == '': return default_idx
        if choice.isdigit() and any(d['index'] == int(choice) for d in input_devices): return int(choice)
        print("Invalid index.")

def audio_callback(indata, frames, time, status):
    if status: print(f"Audio callback status: {status}", file=sys.stderr)
    audio_queue.put(bytes(indata))

def main():
    global is_recording, recorded_frames, silent_frames_count

    config = load_config()
    selected_device = select_audio_device()

    print("\nInitializing services...")
    try:
        vad = webrtcvad.Vad(VAD_AGGRESSIVENESS); print("- VAD initialized.")
        print("- Loading Whisper model...")
        model_name = "openai/whisper-base.en"
        processor = WhisperProcessor.from_pretrained(model_name)
        model = WhisperForConditionalGeneration.from_pretrained(model_name)
        print("- Whisper loaded.")
    except Exception as e:
        sys.exit(f"An error occurred during initialization: {e}")

    max_silent_frames = int(SILENCE_THRESHOLD_S * SAMPLE_RATE / FRAMES_PER_BUFFER)
    
    print(f"\n--- Audio Client Listening... ---")

    try:
        with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=FRAMES_PER_BUFFER, device=selected_device, dtype="int16", channels=1, callback=audio_callback):
            while True:
                frame = audio_queue.get()
                is_speech = vad.is_speech(frame, SAMPLE_RATE)

                if is_recording:
                    recorded_frames.append(frame)
                    if not is_speech and len(recorded_frames) > 10:
                        silent_frames_count += 1
                        if silent_frames_count > max_silent_frames:
                            print("Silence detected, processing...")
                            all_frames = list(pre_buffer_frames) + recorded_frames
                            with wave.open(WAV_FILE_NAME, 'wb') as wf:
                                wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE); wf.writeframes(b''.join(all_frames))
                            
                            try:
                                sr, audio_data = read_wav(WAV_FILE_NAME)
                                audio_data = audio_data.astype(np.float32) / 32768.0
                                input_features = processor(audio_data, sampling_rate=sr, return_tensors="pt").input_features
                                predicted_ids = model.generate(input_features)
                                transcribed_text = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()
                            except Exception as e:
                                transcribed_text = ""
                            
                            if transcribed_text:
                                print(f"Transcribed: '{transcribed_text}'")
                                # The script no longer filters. It sends everything to the MCP.
                                send_to_mcp(transcribed_text, config['mcp_url'])

                            is_recording = False; recorded_frames.clear(); pre_buffer_frames.clear(); silent_frames_count = 0
                            print(f"\n--- Audio Client Listening... ---")
                    else:
                        silent_frames_count = 0
                else:
                    pre_buffer_frames.append(frame)
                    if is_speech:
                        print("Speech detected, recording...")
                        is_recording = True
                        recorded_frames.extend(pre_buffer_frames)
    except KeyboardInterrupt:
        print("\nStopping the script.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()