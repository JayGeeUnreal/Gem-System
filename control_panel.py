import tkinter as tk
from tkinter import ttk
import sounddevice as sd
import numpy as np
import queue
import threading
import time
import math
import os
import configparser
import cv2
from PIL import Image, ImageTk
import traceback
import subprocess  # Required import

# --- Configuration ---
MIN_DB = -60.0
MAX_DB = 0.0
SMOOTHING_FACTOR = 0.85
PEAK_HOLD_DURATION = 1.5
TEST_TONE_FREQUENCY = 440
INI_FILE_PATH = "mcp_settings.ini"
DROPDOWN_SECTION = "MCP"
DROPDOWN_KEY = "llm_choice"
DROPDOWN_OPTIONS = ["gemini", "ollama", "ollama_vision", "minitron"]

class AudioApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Master Control Panel")
        
        # --- Change the window size here ---
        self.geometry("1400x880") 
        
        self.config = configparser.ConfigParser(interpolation=None)
        self.ini_entries = {}
        self.input_audio_queue = queue.Queue()
        self.output_audio_queue = queue.Queue()
        self.video_frame_queue = queue.Queue()
        self.input_stream = None
        self.output_stream = None
        self.is_testing_output = False
        self.output_start_idx = 0
        self.input_smoothed_db = MIN_DB
        self.input_peak_db = MIN_DB
        self.input_peak_hold_time = 0
        self.output_smoothed_db = MIN_DB
        self.output_peak_db = MIN_DB
        self.output_peak_hold_time = 0
        self.vision_thread = None
        self.stop_vision_thread = False

        # --- UI Setup ---
        self.create_widgets()
        self.populate_device_lists()
        self.populate_camera_list()
        self.reload_ini_ui()
        self.process_audio_queues()
        self.process_video_queue()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        audio_ini_tab = ttk.Frame(notebook)
        notebook.add(audio_ini_tab, text="Audio & General Settings")
        
        vision_tab = ttk.Frame(notebook)
        notebook.add(vision_tab, text="Vision Settings")

        neurosync_tab = ttk.Frame(notebook)
        notebook.add(neurosync_tab, text="Neurosync Settings")

        main_paned_window = tk.PanedWindow(audio_ini_tab, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bd=2)
        main_paned_window.pack(fill="both", expand=True)
        left_panel = ttk.Frame(main_paned_window)
        right_panel = ttk.Frame(main_paned_window)
        main_paned_window.add(left_panel, width=450, minsize=400)
        main_paned_window.add(right_panel, minsize=500)
        input_frame = ttk.LabelFrame(left_panel, text="Microphone Input (AI Hearing)", padding=(10, 5))
        input_frame.pack(fill="x", expand=False)
        output_frame = ttk.LabelFrame(left_panel, text="Audio Output (AI Speech)", padding=(10, 5))
        output_frame.pack(pady=10, fill="x", expand=False)
        
        self.setup_input_widgets(input_frame)
        self.setup_output_widgets(output_frame)
        self.setup_ini_widgets(right_panel)
        self.setup_vision_widgets(vision_tab)
        self.setup_neurosync_widgets(neurosync_tab)

    def setup_neurosync_widgets(self, parent_frame):
        # Helper function to create a scrollable frame
        def create_scrollable_frame(parent, text_label):
            ini_frame = ttk.LabelFrame(parent, text=text_label)
            ini_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            canvas = tk.Canvas(ini_frame)
            scrollbar = ttk.Scrollbar(ini_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

            def _on_canvas_configure(event):
                canvas.itemconfig(canvas_window, width=event.width)

            canvas.bind("<Configure>", _on_canvas_configure)
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            scrollbar.pack(side="right", fill="y")
            
            return scrollable_frame

        neurosync_paned_window = tk.PanedWindow(parent_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bd=2)
        neurosync_paned_window.pack(fill="both", expand=True)

        left_pane = ttk.Frame(neurosync_paned_window)
        neurosync_paned_window.add(left_pane, width=500, minsize=400)
        self.neurosync_api_scrollable_frame = create_scrollable_frame(left_pane, "Neurosync Local API")

        right_pane = ttk.Frame(neurosync_paned_window)
        neurosync_paned_window.add(right_pane)
        self.neurosync_main_scrollable_frame = create_scrollable_frame(right_pane, "Neurosync & Watcher")

    def setup_vision_widgets(self, parent_frame):
        vision_paned_window = tk.PanedWindow(parent_frame, orient=tk.VERTICAL, sashrelief=tk.RAISED, bd=2)
        vision_paned_window.pack(fill="both", expand=True, padx=5, pady=5)
        preview_frame = ttk.LabelFrame(vision_paned_window, text="Camera Preview", padding=10)
        vision_paned_window.add(preview_frame, height=480)
        self.video_label = tk.Label(preview_frame, bg="black", text="Preview will appear here", fg="white")
        self.video_label.pack(fill="both", expand=True)
        vision_settings_frame = ttk.Frame(vision_paned_window, padding=(10, 10))
        vision_paned_window.add(vision_settings_frame)
        
        controls_frame = ttk.Frame(vision_settings_frame)
        controls_frame.pack(fill="x", pady=5, anchor="n")
        ttk.Label(controls_frame, text="Available Cameras:").pack(side="left", padx=(0, 10))
        self.camera_combobox = ttk.Combobox(controls_frame, state="readonly", width=10)
        self.camera_combobox.pack(side="left", padx=10)
        start_btn = ttk.Button(controls_frame, text="Start Preview", command=self.start_camera_preview)
        start_btn.pack(side="left", padx=10)
        stop_btn = ttk.Button(controls_frame, text="Stop Preview", command=self.stop_camera_preview)
        stop_btn.pack(side="left", padx=10)
        saved_device_frame = ttk.Frame(vision_settings_frame)
        saved_device_frame.pack(fill="x", pady=5, anchor="n")
        ttk.Label(saved_device_frame, text="Saved Camera Index:").pack(side="left")
        self.saved_camera_device_var = tk.StringVar(value="None")
        ttk.Entry(saved_device_frame, textvariable=self.saved_camera_device_var, state="readonly").pack(side="left", fill="x", expand=True, padx=10)

        vlm_frame = ttk.LabelFrame(vision_settings_frame, text="Vision Language Model Settings", padding=10)
        vlm_frame.pack(fill="x", expand=True, pady=(10, 0), anchor="n")

        ttk.Label(vlm_frame, text="SmolVLM Model ID:").pack(side="left", padx=(0, 10))
        self.smol_vlm_entry = ttk.Entry(vlm_frame)
        self.smol_vlm_entry.pack(side="left", fill="x", expand=True)
        
        self.vision_ini_container = ttk.Frame(vision_settings_frame)
        self.vision_ini_container.pack(fill="both", expand=True, pady=10, anchor="n")

    def setup_ini_widgets(self, parent_frame):
        ini_frame = ttk.LabelFrame(parent_frame, text="mcp_settings.ini (General)")
        ini_frame.pack(fill="both", expand=True)
        
        # Bind mouse events for scrolling
        ini_frame.bind('<Enter>', self._bind_mousewheel_for_right_pane)
        ini_frame.bind('<Leave>', self._unbind_mousewheel_for_right_pane)
        
        self.ini_canvas = tk.Canvas(ini_frame)
        scrollbar = ttk.Scrollbar(ini_frame, orient="vertical", command=self.ini_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.ini_canvas)
        self.canvas_window = self.ini_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.ini_canvas.bind("<Configure>", self._on_canvas_configure)
        self.scrollable_frame.bind("<Configure>", lambda e: self.ini_canvas.configure(scrollregion=self.ini_canvas.bbox("all")))
        self.ini_canvas.configure(yscrollcommand=scrollbar.set)
        self.ini_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")
        
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(fill="x", pady=(5,0))
        
        save_button = ttk.Button(button_frame, text="Save All Settings", command=self.save_ini_file)
        save_button.pack(side="left", expand=True, fill="x", padx=5)
        
        run_neurosync_button = ttk.Button(button_frame, text="1. Neurosync Local API", command=self.run_neurosync_api_script)
        run_neurosync_button.pack(side="left", expand=True, fill="x", padx=5)
        
        run_watcher_button = ttk.Button(button_frame, text="2. Neurosync Watcher To Face", command=self.run_watcher_to_face_script)
        run_watcher_button.pack(side="left", expand=True, fill="x", padx=5)
        
        run_script_button = ttk.Button(button_frame, text="3. MCP", command=self.run_main_script)
        run_script_button.pack(side="left", expand=True, fill="x", padx=5)

        run_styletts2_button = ttk.Button(button_frame, text="4. StyleTTS2", command=self.run_styletts2_script)
        run_styletts2_button.pack(side="left", expand=True, fill="x", padx=5)

        run_vision_button = ttk.Button(button_frame, text="5. Vision", command=self.run_vision_script)
        run_vision_button.pack(side="left", expand=True, fill="x", padx=5)
        
        reload_button = ttk.Button(button_frame, text="Reload All Settings", command=self.reload_ini_ui)
        reload_button.pack(side="left", expand=True, fill="x", padx=5)

    def run_neurosync_api_script(self):
        """Runs the neurosync local API .bat file in a new process."""
        subfolder_name = "start_scripts"
        bat_file_name = "start_neurosync_localapi.bat" 
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bat_file_path = os.path.join(script_dir, subfolder_name, bat_file_name)
        
        print(f"Attempting to run: {bat_file_path}")
        try:
            subprocess.Popen(bat_file_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
            print(f"Successfully launched {bat_file_name} in a new console.")
        except FileNotFoundError:
            print(f"Error: The file '{bat_file_path}' was not found.")
            from tkinter import messagebox
            messagebox.showerror("Error", f"Could not find the batch file:\n{bat_file_path}")
        except Exception as e:
            print(f"An error occurred while trying to run the batch file: {e}")
            from tkinter import messagebox
            messagebox.showerror("Error", f"An error occurred while launching the script:\n{e}")

    def run_watcher_to_face_script(self):
        """Runs the neurosync watcher to face .bat file in a new process."""
        subfolder_name = "start_scripts"
        bat_file_name = "start_neurosync_watcher_to_face.bat" 
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bat_file_path = os.path.join(script_dir, subfolder_name, bat_file_name)
        
        print(f"Attempting to run: {bat_file_path}")
        try:
            subprocess.Popen(bat_file_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
            print(f"Successfully launched {bat_file_name} in a new console.")
        except FileNotFoundError:
            print(f"Error: The file '{bat_file_path}' was not found.")
            from tkinter import messagebox
            messagebox.showerror("Error", f"Could not find the batch file:\n{bat_file_path}")
        except Exception as e:
            print(f"An error occurred while trying to run the batch file: {e}")
            from tkinter import messagebox
            messagebox.showerror("Error", f"An error occurred while launching the script:\n{e}")

    def run_main_script(self):
        """Runs the MCP .bat file from a specific subfolder in a new process."""
        subfolder_name = "start_scripts"
        bat_file_name = "start_mcp.bat" 
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bat_file_path = os.path.join(script_dir, subfolder_name, bat_file_name)
        
        print(f"Attempting to run: {bat_file_path}")
        try:
            subprocess.Popen(bat_file_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
            print("Successfully launched the batch file in a new console.")
        except FileNotFoundError:
            print(f"Error: The file '{bat_file_path}' was not found.")
            from tkinter import messagebox
            messagebox.showerror("Error", f"Could not find the batch file:\n{bat_file_path}")
        except Exception as e:
            print(f"An error occurred while trying to run the batch file: {e}")
            from tkinter import messagebox
            messagebox.showerror("Error", f"An error occurred while launching the script:\n{e}")
            
    def run_styletts2_script(self):
        """Runs the Start_StyleTTS2.bat file in a new process."""
        subfolder_name = "start_scripts"
        bat_file_name = "Start_StyleTTS2.bat" 
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bat_file_path = os.path.join(script_dir, subfolder_name, bat_file_name)
        
        print(f"Attempting to run: {bat_file_path}")
        try:
            subprocess.Popen(bat_file_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
            print(f"Successfully launched {bat_file_name} in a new console.")
        except FileNotFoundError:
            print(f"Error: The file '{bat_file_path}' was not found.")
            from tkinter import messagebox
            messagebox.showerror("Error", f"Could not find the batch file:\n{bat_file_path}")
        except Exception as e:
            print(f"An error occurred while trying to run the batch file: {e}")
            from tkinter import messagebox
            messagebox.showerror("Error", f"An error occurred while launching the script:\n{e}")
            
    def run_vision_script(self):
        """Runs the start_vision.bat file in a new process."""
        subfolder_name = "start_scripts"
        bat_file_name = "start_vision.bat" 
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bat_file_path = os.path.join(script_dir, subfolder_name, bat_file_name)
        
        print(f"Attempting to run: {bat_file_path}")
        try:
            subprocess.Popen(bat_file_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
            print(f"Successfully launched {bat_file_name} in a new console.")
        except FileNotFoundError:
            print(f"Error: The file '{bat_file_path}' was not found.")
            from tkinter import messagebox
            messagebox.showerror("Error", f"Could not find the batch file:\n{bat_file_path}")
        except Exception as e:
            print(f"An error occurred while trying to run the batch file: {e}")
            from tkinter import messagebox
            messagebox.showerror("Error", f"An error occurred while launching the script:\n{e}")

    def _on_right_pane_mousewheel(self, event):
        """Handles the mouse wheel scroll event for the right settings pane."""
        if event.num == 5 or event.delta < 0:
            self.ini_canvas.yview_scroll(1, "units")
        if event.num == 4 or event.delta > 0:
            self.ini_canvas.yview_scroll(-1, "units")

    def _bind_mousewheel_for_right_pane(self, event):
        """Binds the mouse wheel event to the scroll function."""
        self.bind_all("<MouseWheel>", self._on_right_pane_mousewheel)

    def _unbind_mousewheel_for_right_pane(self, event):
        """Unbinds the mouse wheel event."""
        self.unbind_all("<MouseWheel>")

    def _on_canvas_configure(self, event):
        canvas_width = event.width
        self.ini_canvas.itemconfig(self.canvas_window, width=canvas_width)

    def _read_ini_safely(self):
        self.config = configparser.ConfigParser(interpolation=None)
        try:
            with open(INI_FILE_PATH, 'r', encoding='utf-8') as f: lines = f.readlines()
        except FileNotFoundError: return False, f"File not found: {INI_FILE_PATH}"
        current_section = None; i = 0
        while i < len(lines):
            line = lines[i]; stripped_line = line.strip()
            if not stripped_line or stripped_line.startswith(('#', ';')): i += 1; continue
            if stripped_line.startswith('[') and stripped_line.endswith(']'):
                current_section = stripped_line[1:-1]
                if not self.config.has_section(current_section): self.config.add_section(current_section)
                i += 1; continue
            if current_section and '=' in stripped_line:
                key, value = stripped_line.split('=', 1); key = key.strip()
                full_value_lines = [value.strip()]
                while i + 1 < len(lines) and lines[i + 1].startswith((' ', '\t')):
                    i += 1; full_value_lines.append(lines[i].strip())
                full_value = '\n'.join(full_value_lines)
                self.config.set(current_section, key, full_value)
            i += 1
        return True, ""

    def reload_ini_ui(self):
        for container_name in ['scrollable_frame', 'vision_ini_container', 
                               'neurosync_api_scrollable_frame', 'neurosync_main_scrollable_frame']:
            container = getattr(self, container_name, None)
            if container:
                for widget in container.winfo_children():
                    widget.destroy()
        self.ini_entries.clear()

        success, error_message = self._read_ini_safely()
        if not success:
            if hasattr(self, 'scrollable_frame'):
                ttk.Label(self.scrollable_frame, text=f"Error reading INI file: {error_message}").pack()
            return

        section_container_map = {
            'VisionService': self.vision_ini_container,
            'NeurosyncLocalAPI': self.neurosync_api_scrollable_frame,
            'Neurosync': self.neurosync_main_scrollable_frame,
            'Watcher': self.neurosync_main_scrollable_frame,
            'LiveLink': self.neurosync_main_scrollable_frame,
        }
        default_container = self.scrollable_frame
        manual_sections = {'Audio'} 

        for section in self.config.sections():
            if section in manual_sections:
                continue

            parent_container = section_container_map.get(section, default_container)
            
            if not parent_container:
                print(f"Warning: Could not find a valid container for section '{section}'. Skipping.")
                continue

            self.ini_entries[section] = {}
            section_frame = ttk.LabelFrame(parent_container, text=section, padding=10)

            for key in self.config.options(section):
                if (section == 'VisionService' and key in ('camera_index', 'smol_vlm_model_id')):
                    continue
                
                value = self.config.get(section, key)
                row_frame = ttk.Frame(section_frame); row_frame.pack(fill="x", pady=2, padx=2)
                label = ttk.Label(row_frame, text=f"{key}:", width=20); label.pack(side="left", anchor="n", pady=2)
                
                widget = None
                # --- MODIFICATION START ---
                # Check if the key name suggests it's a secret value
                secret_keywords = ['api_key', 'secret', 'session_id', 'rapidapi_key']
                is_secret_field = any(keyword in key.lower() for keyword in secret_keywords)

                if section == DROPDOWN_SECTION and key == DROPDOWN_KEY:
                    widget = ttk.Combobox(row_frame, values=DROPDOWN_OPTIONS, state="readonly")
                    if value in DROPDOWN_OPTIONS: widget.set(value)
                elif '\n' in value:
                    widget = tk.Text(row_frame, height=8, wrap="word")
                    widget.insert("1.0", value)
                else:
                    widget = ttk.Entry(row_frame)
                    widget.insert(0, value)
                    # If it's a secret field, hide the text and add a "Show" button
                    if is_secret_field:
                        widget.config(show="*")
                        show_var = tk.BooleanVar(value=False)
                        
                        # This command toggles the 'show' option of the widget
                        toggle_command = lambda w=widget, v=show_var: w.config(show="" if v.get() else "*")
                        
                        show_hide_btn = ttk.Checkbutton(row_frame, text="Show", variable=show_var, command=toggle_command)
                        show_hide_btn.pack(side="right", padx=(5, 0))
                # --- MODIFICATION END ---
                
                if widget:
                    widget.pack(side="left", fill="x", expand=True)
                    self.ini_entries[section][key] = widget
            
            if section_frame.winfo_children():
                section_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        try:
            if self.config.has_section('Audio'):
                self.selected_input_device_var.set(self.config.get('Audio', 'selected_input', fallback='None'))
                self.selected_output_device_var.set(self.config.get('Audio', 'selected_output', fallback='None'))
            if self.config.has_section('VisionService'):
                saved_index = self.config.get('VisionService', 'camera_index', fallback='None')
                self.saved_camera_device_var.set(saved_index)
                if saved_index in self.camera_combobox['values']:
                    self.camera_combobox.set(saved_index)
                
                vlm_model_id = self.config.get('VisionService', 'smol_vlm_model_id', fallback='HuggingFaceTB/SmolVLM-500M-Instruct')
                if hasattr(self, 'smol_vlm_entry'):
                    self.smol_vlm_entry.delete(0, tk.END)
                    self.smol_vlm_entry.insert(0, vlm_model_id)
        except Exception as e: 
            print(f"Error loading dedicated settings: {e}")


    def save_ini_file(self):
        settings_to_update = {}
        for section, keys in self.ini_entries.items():
            settings_to_update[section] = {}
            for key, widget in keys.items():
                value = widget.get("1.0", tk.END).strip() if isinstance(widget, tk.Text) else widget.get()
                settings_to_update[section][key] = value
        settings_to_update['Audio'] = {
            'selected_input': self.selected_input_device_var.get(),
            'selected_output': self.selected_output_device_var.get()
        }
        
        if 'VisionService' not in settings_to_update: 
            settings_to_update['VisionService'] = {}
        
        selected_cam_idx = self.camera_combobox.get()
        settings_to_update['VisionService']['camera_index'] = selected_cam_idx if selected_cam_idx else "None"

        if hasattr(self, 'smol_vlm_entry'):
            settings_to_update['VisionService']['smol_vlm_model_id'] = self.smol_vlm_entry.get()

        try:
            with open(INI_FILE_PATH, 'r', encoding='utf-8') as f: lines = f.readlines()
        except FileNotFoundError: lines = []
        new_lines = []; current_section = None; sections_found = set(); i = 0
        while i < len(lines):
            line = lines[i]; stripped_line = line.strip()
            if stripped_line.startswith('[') and stripped_line.endswith(']'):
                current_section = stripped_line[1:-1]; sections_found.add(current_section)
                new_lines.append(line); i += 1
            elif current_section and '=' in stripped_line and not stripped_line.startswith(('#', ';')):
                key = stripped_line.split('=')[0].strip()
                original_block_end_index = i + 1
                while original_block_end_index < len(lines) and lines[original_block_end_index].strip() and lines[original_block_end_index].startswith((' ', '\t')): original_block_end_index += 1
                if current_section in settings_to_update and key in settings_to_update[current_section]:
                    new_val = settings_to_update[current_section][key]
                    if '\n' in new_val:
                        first_line, rest = new_val.split('\n', 1)
                        indented_rest = '\n'.join(['  ' + l.strip() for l in rest.split('\n')])
                        final_val = first_line + '\n' + indented_rest
                    else: final_val = new_val
                    indentation = line[:len(line) - len(line.lstrip())]
                    new_lines.append(f"{indentation}{key} = {final_val}\n")
                    del settings_to_update[current_section][key]
                    if not settings_to_update[current_section]: del settings_to_update[current_section]
                    i = original_block_end_index
                else: new_lines.append(line); i += 1
            else: new_lines.append(line); i += 1
        if settings_to_update:
            for section, keys in settings_to_update.items():
                if section not in sections_found:
                    if new_lines and not new_lines[-1].strip() == "": new_lines.append("\n")
                    new_lines.append(f"[{section}]\n")
                for key, value in keys.items():
                    if '\n' in value:
                        first_line, rest = value.split('\n', 1)
                        indented_rest = '\n'.join(['  ' + l.strip() for l in rest.split('\n')])
                        value = first_line + '\n' + indented_rest
                    new_lines.append(f"{key} = {value}\n")
        try:
            with open(INI_FILE_PATH, 'w', encoding='utf-8') as f: f.writelines(new_lines)
            print("Settings successfully saved, preserving comments and format!")
            self.reload_ini_ui()
        except Exception as e: print(f"Error writing to file: {e}")

    def populate_camera_list(self):
        available_cameras = []
        backend_to_use = cv2.CAP_DSHOW
        try:
            for i in range(10):
                cap = cv2.VideoCapture(i, backend_to_use)
                if cap is not None and cap.isOpened():
                    available_cameras.append(str(i))
                    cap.release()
        except Exception:
            print("="*60)
            print("A CRITICAL ERROR occurred while initializing the camera with DSHOW.")
            traceback.print_exc()
            print("="*60)
        self.camera_combobox['values'] = available_cameras
        if available_cameras:
            print(f"Found DSHOW cameras: {available_cameras}")
        else:
            print("No cameras could be opened with the DSHOW backend.")

    def start_camera_preview(self):
        if self.vision_thread is not None and self.vision_thread.is_alive(): return
        cam_index_str = self.camera_combobox.get()
        if not cam_index_str: return
        cam_index = int(cam_index_str)
        self.stop_vision_thread = False
        self.vision_thread = threading.Thread(target=self._video_capture_loop, args=(cam_index,), daemon=True)
        self.vision_thread.start()

    def stop_camera_preview(self):
        if self.vision_thread is not None and self.vision_thread.is_alive():
            self.stop_vision_thread = True
        self.video_label.config(image='', text="Preview stopped", fg="white")
        self.video_label.image = None

    def _video_capture_loop(self, camera_index):
        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print(f"Error: Could not open camera index {camera_index} with DSHOW.")
            self.video_frame_queue.put(f"Failed to open camera {camera_index}")
            return
        while not self.stop_vision_thread:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue
            rgb_frame = cv2.cvtColor(frame, cv.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_frame)
            try:
                self.video_frame_queue.put_nowait(pil_img)
            except queue.Full:
                pass
        cap.release()

    def process_video_queue(self):
        try:
            item = self.video_frame_queue.get_nowait()
            if isinstance(item, str):
                self.video_label.config(image='', text=item, fg="red")
                self.video_label.image = None
                return
            label_w = self.video_label.winfo_width()
            label_h = self.video_label.winfo_height()
            if label_w > 1 and label_h > 1:
                item.thumbnail((label_w, label_h), Image.Resampling.LANCZOS)
                photo_image = ImageTk.PhotoImage(image=item)
                self.video_label.config(image=photo_image, text="")
                self.video_label.image = photo_image
        except queue.Empty:
            pass
        finally:
            self.after(30, self.process_video_queue)

    def on_closing(self):
        print("Closing application: Signaling threads to stop...")
        self.stop_vision_thread = True
        self.is_testing_output = False
        if self.input_stream:
            self.input_stream.close()
        if self.output_stream:
            self.output_stream.close()
        print("Destroying UI and exiting.")
        self.destroy()

    def populate_device_lists(self):
        try:
            devices = sd.query_devices()
            
            self.input_listbox.delete(0, tk.END)
            self.output_listbox.delete(0, tk.END)

            for i, d in enumerate(devices):
                device_name = d['name']
                
                if not device_name.strip().endswith("Voic"):
                    if d['max_input_channels'] > 0:
                        self.input_listbox.insert(tk.END, f"[{i}] {device_name}")
                    if d['max_output_channels'] > 0:
                        self.output_listbox.insert(tk.END, f"[{i}] {device_name}")

        except Exception as e:
            print(f"Error querying devices: {e}")

    def setup_input_widgets(self, parent_frame):
        device_frame = ttk.Frame(parent_frame); device_frame.pack(pady=5, fill="x")
        ttk.Label(device_frame, text="Selected Input Device:").pack(side="left", padx=(0, 10))
        self.selected_input_device_var = tk.StringVar(value="None")
        ttk.Entry(device_frame, textvariable=self.selected_input_device_var, state="readonly").pack(side="left", fill="x", expand=True)
        list_frame = ttk.Frame(parent_frame); list_frame.pack(pady=10, fill="both", expand=True)
        ttk.Label(list_frame, text="Mic device list (Double-click to select):").pack(anchor="w")
        self.input_listbox = tk.Listbox(list_frame, exportselection=False); self.input_listbox.pack(side="left", fill="both", expand=True)
        self.input_listbox.bind("<Double-Button-1>", self.on_input_device_select)
        ttk.Label(parent_frame, text="Input VU Meter:").pack(anchor="w", pady=(10, 0))
        self.input_vu_meter_canvas = tk.Canvas(parent_frame, height=30, bg="lightgrey", relief="sunken", borderwidth=1); self.input_vu_meter_canvas.pack(pady=5, fill="x")

    def setup_output_widgets(self, parent_frame):
        device_frame = ttk.Frame(parent_frame); device_frame.pack(pady=5, fill="x")
        ttk.Label(device_frame, text="Selected Output Device:").pack(side="left", padx=(0, 10))
        self.selected_output_device_var = tk.StringVar(value="None")
        ttk.Entry(device_frame, textvariable=self.selected_output_device_var, state="readonly").pack(side="left", fill="x", expand=True)
        list_frame = ttk.Frame(parent_frame); list_frame.pack(pady=10, fill="both", expand=True)
        ttk.Label(list_frame, text="Output device list (Double-click to select):").pack(anchor="w")
        self.output_listbox = tk.Listbox(list_frame, exportselection=False); self.output_listbox.pack(side="left", fill="both", expand=True)
        self.output_listbox.bind("<Double-Button-1>", self.on_output_device_select)
        self.test_output_button = ttk.Button(list_frame, text="Test", command=self.toggle_output_test, width=10); self.test_output_button.pack(side="left", padx=(10, 0), anchor="n")
        ttk.Label(parent_frame, text="Output Test VU Meter:").pack(anchor="w", pady=(10, 0))
        self.output_vu_meter_canvas = tk.Canvas(parent_frame, height=30, bg="lightgrey", relief="sunken", borderwidth=1); self.output_vu_meter_canvas.pack(pady=5, fill="x")

    def on_input_device_select(self, event):
        selection_indices = self.input_listbox.curselection()
        if not selection_indices: return
        selected_text = self.input_listbox.get(selection_indices[0])
        self.selected_input_device_var.set(selected_text)
        device_id = int(selected_text.split(']')[0][1:])
        self.start_input_stream(device_id)

    def on_output_device_select(self, event):
        selection_indices = self.output_listbox.curselection()
        if not selection_indices: return
        selected_text = self.output_listbox.get(selection_indices[0])
        self.selected_output_device_var.set(selected_text)

    def toggle_output_test(self):
        if self.is_testing_output: self.stop_output_test()
        else:
            selected_text = self.selected_output_device_var.get()
            if selected_text == "None" or "[" not in selected_text: return
            device_id = int(selected_text.split(']')[0][1:])
            self.start_output_test(device_id)

    def start_input_stream(self, device_id):
        if self.input_stream: self.input_stream.close()
        try:
            samplerate = sd.query_devices(device_id, 'input')['default_samplerate']
            self.input_stream = sd.InputStream(device=device_id, channels=1, samplerate=samplerate, callback=self.input_audio_callback)
            threading.Thread(target=self.input_stream.start, daemon=True).start()
        except Exception as e: print(f"Error starting input stream: {e}")

    def input_audio_callback(self, indata, frames, time_info, status):
        rms = np.sqrt(np.mean(indata**2)); current_db = 20 * math.log10(rms) if rms > 0 else MIN_DB
        self.input_audio_queue.put(current_db)

    def start_output_test(self, device_id):
        self.is_testing_output = True; self.test_output_button.config(text="Stop")
        try:
            samplerate = sd.query_devices(device_id, 'output')['default_samplerate']
            self.output_stream = sd.OutputStream(device=device_id, channels=1, samplerate=samplerate, callback=self.output_audio_callback)
            threading.Thread(target=self.output_stream.start, daemon=True).start()
        except Exception as e: print(f"Error starting output test: {e}"); self.stop_output_test()

    def stop_output_test(self):
        if self.output_stream: self.output_stream.close()
        self.output_stream = None; self.is_testing_output = False
        self.test_output_button.config(text="Test")
        self.output_smoothed_db = MIN_DB; self.output_peak_db = MIN_DB

    def output_audio_callback(self, outdata, frames, time_info, status):
        t = (self.output_start_idx + np.arange(frames)) / self.output_stream.samplerate; t = t.reshape(-1, 1)
        waveform = 0.5 * np.sin(2 * np.pi * TEST_TONE_FREQUENCY * t); outdata[:] = waveform
        self.output_start_idx += frames
        rms = np.sqrt(np.mean(waveform**2)); current_db = 20 * math.log10(rms) if rms > 0 else MIN_DB
        self.output_audio_queue.put(current_db)

    def process_audio_queues(self):
        try:
            while not self.input_audio_queue.empty():
                current_db = self.input_audio_queue.get_nowait()
                self.input_smoothed_db = (SMOOTHING_FACTOR * self.input_smoothed_db) + ((1 - SMOOTHING_FACTOR) * current_db)
                if self.input_smoothed_db > self.input_peak_db: self.input_peak_db = self.input_smoothed_db; self.input_peak_hold_time = time.time()
        except queue.Empty: pass
        if time.time() - self.input_peak_hold_time > PEAK_HOLD_DURATION: self.input_peak_db = max(self.input_smoothed_db, self.input_peak_db - 2)
        try:
            while not self.output_audio_queue.empty():
                current_db = self.output_audio_queue.get_nowait()
                self.output_smoothed_db = (SMOOTHING_FACTOR * self.output_smoothed_db) + ((1 - SMOOTHING_FACTOR) * current_db)
                if self.output_smoothed_db > self.output_peak_db: self.output_peak_db = self.output_smoothed_db; self.output_peak_hold_time = time.time()
        except queue.Empty: pass
        if self.is_testing_output:
            if time.time() - self.output_peak_hold_time > PEAK_HOLD_DURATION: self.output_peak_db = max(self.output_smoothed_db, self.output_peak_db - 2)
        else: self.output_smoothed_db = max(MIN_DB, self.output_smoothed_db - 3); self.output_peak_db = max(self.output_smoothed_db, self.output_peak_db - 3)
        self.update_vu_meter_canvas(self.input_vu_meter_canvas, self.input_smoothed_db, self.input_peak_db)
        self.update_vu_meter_canvas(self.output_vu_meter_canvas, self.output_smoothed_db, self.output_peak_db)
        self.after(50, self.process_audio_queues)

    def update_vu_meter_canvas(self, canvas, smoothed_db, peak_db):
        width, height = canvas.winfo_width(), canvas.winfo_height()
        if width <= 1: return
        canvas.delete("all")
        clamped_db = max(MIN_DB, min(smoothed_db, MAX_DB)); bar_length = int(((clamped_db - MIN_DB) / (MAX_DB - MIN_DB)) * width)
        green_w, yellow_w = int(width * 0.7), int(width * 0.9)
        if bar_length > 0: canvas.create_rectangle(0, 0, min(bar_length, green_w), height, fill="#4CAF50", width=0)
        if bar_length > green_w: canvas.create_rectangle(green_w, 0, min(bar_length, yellow_w), height, fill="#FFC107", width=0)
        if bar_length > yellow_w: canvas.create_rectangle(yellow_w, 0, bar_length, height, fill="#F44336", width=0)
        clamped_peak_db = max(MIN_DB, min(peak_db, MAX_DB)); peak_pos = int(((clamped_peak_db - MIN_DB) / (MAX_DB - MIN_DB)) * width)
        if peak_pos > 1: canvas.create_line(peak_pos, 0, peak_pos, height, fill="black", width=2)
        canvas.create_text(width - 10, height / 2, text=f"{smoothed_db:.2f} dB", anchor="e", fill="black")

if __name__ == "__main__":
    if not os.path.exists(INI_FILE_PATH):
        with open(INI_FILE_PATH, "w", encoding='utf-8') as f:
            f.write("[General]\n"
                    "setting1 = value1\n\n"
                    "[SomeService]\n"
                    "# These keys will be hidden automatically by the UI\n"
                    "my_secret_session_id = some_secret_value_12345\n"
                    "my_rapidapi_key = another_secret_value_67890\n\n"
                    "[Audio]\n"
                    "selected_input = None\n"
                    "selected_output = None\n\n"
                    "[VisionService]\n"
                    "camera_index = None\n"
                    "smol_vlm_model_id = HuggingFaceTB/SmolVLM-500M-Instruct\n\n"
                    "[Watcher]\n"
                    "# This must be the full, absolute path to the audio file created by your Flask server.\n"
                    "# Use forward slashes (/) or double backslashes (\\\\) for the path.\n"
                    "target_file_path = C:/Users/your_user/Documents/AI/Gem-System/StyleTTS2/server_output.wav\n\n"
                    "[Neurosync]\n"
                    "neurosync_local_url = http://127.0.0.1:9000/audio_to_blendshapes\n\n"
                    "[NeurosyncLocalAPI]\n"
                    "host = 127.0.0.1\n"
                    "port = 9000\n"
                    "endpoint_url = http://127.0.0.1:5000\n"
                    "timeout_seconds = 60\n"
                    "enable_logging = true\n\n"
                    "[LiveLink]\n"
                    "ip = 192.168.1.101\n"
                    "port = 11111\n\n"
                    f"[{DROPDOWN_SECTION}]\n"
                    f"{DROPDOWN_KEY} = gemini\n"
                    "# This api_key will also be hidden\n"
                    "gemini_api_key = YOUR_API_KEY_GOES_HERE\n")
            
    app = AudioApp()
    app.mainloop()