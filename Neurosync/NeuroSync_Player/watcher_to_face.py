import os
import pygame
import warnings
import time
import configparser
import sys
from threading import Thread

# --- Import sounddevice for audio device selection ---
try:
    import sounddevice as sd
except ImportError:
    print("FATAL ERROR: The 'sounddevice' library is required. Please install it using: pip install sounddevice")
    sys.exit(1)

# --- Suppress specific warnings ---
warnings.filterwarnings(
    "ignore", 
    message="Couldn't find ffmpeg or avconv - defaulting to ffmpeg, but may not work"
)

# --- Import project-specific modules ---
from livelink.connect.livelink_init import create_socket_connection, initialize_py_face
from livelink.animations.default_animation import default_animation_loop, stop_default_animation
from utils.files.file_utils import initialize_directories
from utils.audio_face_workers import process_wav_file
from utils.emote_sender.send_emote import EmoteConnect

# --- Configuration ---
ENABLE_EMOTE_CALLS = False

# --- NEW: Robust, portable method to find the project root ---
def find_project_root(marker_file='.project_root'):
    """A verbose function to find the project root and print its steps."""
    print("\n--- Starting Root Discovery ---")
    try:
        # 1. Print the script's own path
        script_path = os.path.abspath(__file__)
        print(f"Script path is: {script_path}")
        current_dir = os.path.dirname(script_path)
        print(f"Starting search in: {current_dir}")
    except NameError:
        print("Could not determine script path using __file__. Using current working directory.")
        current_dir = os.getcwd()

    # 2. Loop and print every step
    limit = 10 # Safety break to prevent infinite loops
    for i in range(limit):
        print(f"Checking for anchor in: {current_dir}")
        if os.path.exists(os.path.join(current_dir, marker_file)):
            print(f"✅ FOUND ANCHOR! Project root is: {current_dir}")
            print("--- Root Discovery Complete ---\n")
            return current_dir
        
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            print("❌ Reached top of filesystem. Anchor not found.")
            break
        current_dir = parent_dir
    
    print("--- Root Discovery Failed ---\n")
    return None

root_dir = find_project_root()
if not root_dir:
    # This will stop the script with a clear error if the anchor file is missing.
    raise FileNotFoundError("Could not find the project root. Make sure a '.project_root' file exists in your main 'Gem-System' folder.")

# Construct the full path to the settings file
SETTINGS_FILE = os.path.join(root_dir, 'mcp_settings.ini')


def get_playback_device_from_ini(config):
    """
    Reads the selected audio output device from the [Audio] section of the INI file.
    """
    print("--- Reading audio device from settings ---")
    try:
        device_str = config.get('Audio', 'selected_output')
        
        if device_str is None or device_str.lower() == 'none' or ']' not in device_str:
            print("❌ Audio output device is not set in mcp_settings.ini. Please configure it in the control panel.")
            return None
            
        device_name = device_str.split('] ', 1)[1]
        return device_name
        
    except (configparser.NoSectionError, configparser.NoOptionError):
        print(f"❌ FATAL ERROR: Could not find [Audio] section or 'selected_output' in '{SETTINGS_FILE}'.")
        print("   Please run the Master Control Panel first to select an audio device and save the settings.")
        return None
    except Exception as e:
        print(f"❌ An unexpected error occurred while reading the audio device: {e}")
        return None

def delete_file_with_retry(filepath, max_retries=5, delay=0.2):
    """
    Attempts to delete a file, retrying on failure to handle file locks.
    """
    for attempt in range(max_retries):
        try:
            os.remove(filepath)
            print(f"✅ Deleted '{os.path.basename(filepath)}'. Waiting for next file...")
            return True
        except PermissionError:
            print(f"Attempt {attempt + 1}/{max_retries}: Could not delete file, it's locked. Retrying in {delay}s...")
            time.sleep(delay)
        except FileNotFoundError:
            print(f"File '{os.path.basename(filepath)}' was already deleted.")
            return True
        except Exception as e:
            print(f"❌ An unexpected error occurred while trying to delete the file: {e}")
            return False
    
    print(f"❌ FAILED to delete file '{os.path.basename(filepath)}' after {max_retries} attempts.")
    return False

if __name__ == "__main__":
    
    config = configparser.ConfigParser()
    if not os.path.exists(SETTINGS_FILE):
        # This error is now more informative thanks to the root finder
        print(f"❌ FATAL ERROR: The settings file was not found at the expected path: '{SETTINGS_FILE}'")
        sys.exit(1)
        
    config.read(SETTINGS_FILE)
    
    try:
        target_file_path = config.get('Watcher', 'target_file_path')
        selected_device_name = get_playback_device_from_ini(config)
        print(f"DEBUG: The loaded audio device is: {selected_device_name}")
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        print(f"❌ FATAL ERROR: A required setting is missing from '{SETTINGS_FILE}'. Details: {e}")
        sys.exit(1)

    if selected_device_name is None:
        print("Could not determine audio device from settings. Exiting.")
        sys.exit(1)
    
    print(f"\n✅ Using audio device from settings: '{selected_device_name}'")

    try:
        pygame.mixer.pre_init(44100, -16, 2, 512, devicename=selected_device_name)
        pygame.init()
        print("✅ Pygame audio mixer initialized successfully.")
    except Exception as e:
        print(f"❌ FATAL ERROR: Could not initialize Pygame audio on the selected device. Error: {e}")
        sys.exit(1)

    initialize_directories()
    py_face = initialize_py_face()
    socket_connection = create_socket_connection()
    
    default_animation_thread = Thread(target=default_animation_loop, args=(py_face,))
    default_animation_thread.start()

    print("--- Automatic Processor Started (Definitive Deletion Mode) ---")
    print(f"Watching for file: {target_file_path}")
    print("Send a request to your TTS server to begin. Press Ctrl+C to stop.")

    try:
        while True:
            if os.path.exists(target_file_path):
                print(f"\n✅ File '{os.path.basename(target_file_path)}' detected. Verifying it's complete...")
                
                last_size = os.path.getsize(target_file_path)
                time.sleep(0.1) 
                while last_size != os.path.getsize(target_file_path):
                    last_size = os.path.getsize(target_file_path)
                    print("   - File is still being written, waiting...")
                    time.sleep(0.1)
                
                print("✅ File is stable. Processing...")
                
                if ENABLE_EMOTE_CALLS:
                    EmoteConnect.send_emote("startspeaking")
                
                try:
                    process_wav_file(target_file_path, py_face, socket_connection, default_animation_thread)
                    print("✅ Processing complete.")
                except Exception as e:
                    print(f"❌ An error occurred during processing: {e}")
                finally:
                    if ENABLE_EMOTE_CALLS:
                        EmoteConnect.send_emote("stopspeaking")
                    
                    try:
                        if pygame.mixer.get_init():
                            print("Unloading audio from Pygame to release file lock...")
                            pygame.mixer.music.stop()
                            pygame.mixer.music.unload()
                            print("File lock released.")
                    except Exception as e:
                        print(f"Warning during Pygame unload: {e}")

                    delete_file_with_retry(target_file_path)
            
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping the watcher script.")

    finally:
        print("Cleaning up resources...")
        stop_default_animation.set()
        if default_animation_thread and default_animation_thread.is_alive():
            default_animation_thread.join()
        pygame.quit()
        socket_connection.close()
        print("Cleanup complete. Exiting.")