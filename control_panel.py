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
import subprocess
from tkinter import messagebox
import sys
from youtubesearchpython import VideosSearch # <-- NEW: Import for YouTube search

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
SENSITIVE_KEYS = ["api_key", "session_id"] 

class AudioApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Master Control Panel")
        self.geometry("1400x880") 
        
        self.config = configparser.ConfigParser(interpolation=None)
        self.ini_entries = {}
        self.sensitive_values = {}
        self.input_audio_queue = queue.Queue()
        self.output_audio_queue = queue.Queue()
        self.video_frame_queue = queue.Queue()
        # --- NEW: Queue for handling music search results ---
        self.music_search_results_queue = queue.Queue()
        
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

        self.create_widgets()
        self.populate_device_lists()
        self.populate_camera_list()
        self.reload_ini_ui()
        self.process_audio_queues()
        self.process_video_queue()
        # --- NEW: Start the processor for the music search results ---
        self.process_music_search_queue()
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

        # --- NEW: Create and add the Music Requests tab ---
        music_requests_tab = ttk.Frame(notebook)
        notebook.add(music_requests_tab, text="Music Requests")
        
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
        # --- NEW: Call the setup method for the new tab ---
        self.setup_music_requests_widgets(music_requests_tab)


    # --- NEW: All code for the Music Requests tab is below ---

    def setup_music_requests_widgets(self, parent_frame):
        """Creates all the widgets for the Music Requests tab."""
        # Main frame for the search controls
        search_controls_frame = ttk.LabelFrame(parent_frame, text="YouTube Song Search", padding=10)
        search_controls_frame.pack(fill="x", padx=10, pady=10)
        
        # --- Input Fields ---
        # Song Title
        ttk.Label(search_controls_frame, text="Song Title:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.song_title_entry = ttk.Entry(search_controls_frame, width=40)
        self.song_title_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Artist
        ttk.Label(search_controls_frame, text="Artist:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.artist_entry = ttk.Entry(search_controls_frame, width=40)
        self.artist_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Optional Keywords
        ttk.Label(search_controls_frame, text="Optional Keywords:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.optional_keywords_entry = ttk.Entry(search_controls_frame, width=40)
        self.optional_keywords_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # --- Search Button ---
        search_button = ttk.Button(search_controls_frame, text="Search on YouTube", command=self.start_music_search)
        search_button.grid(row=1, column=2, rowspan=2, padx=10, pady=5, sticky="ns")
        
        search_controls_frame.grid_columnconfigure(1, weight=1) # Makes the entry column expandable

        # --- Results Display ---
        results_frame = ttk.LabelFrame(parent_frame, text="Search Results", padding=10)
        results_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Create the Treeview (table)
        columns = ("#", "title", "channel", "duration", "link")
        self.music_results_treeview = ttk.Treeview(results_frame, columns=columns, show="headings", height=15)
        
        # Define column headings
        self.music_results_treeview.heading("#", text="#", anchor="center")
        self.music_results_treeview.heading("title", text="Title")
        self.music_results_treeview.heading("channel", text="Channel", anchor="center")
        self.music_results_treeview.heading("duration", text="Duration", anchor="center")
        self.music_results_treeview.heading("link", text="Link")
        
        # Define column widths
        self.music_results_treeview.column("#", width=30, stretch=False, anchor="center")
        self.music_results_treeview.column("title", width=400)
        self.music_results_treeview.column("channel", width=150)
        self.music_results_treeview.column("duration", width=80, stretch=False, anchor="center")
        self.music_results_treeview.column("link", width=350)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.music_results_treeview.yview)
        self.music_results_treeview.configure(yscrollcommand=scrollbar.set)
        
        self.music_results_treeview.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def start_music_search(self):
        """Starts the YouTube search in a background thread to prevent GUI freezing."""
        # Get user input from the entry fields
        song = self.song_title_entry.get().strip()
        artist = self.artist_entry.get().strip()
        optional = self.optional_keywords_entry.get().strip()

        if not song and not artist:
            messagebox.showwarning("Empty Search", "Please enter a song title or artist to search for.")
            return

        # Clear the previous results and show a "searching" message
        for i in self.music_results_treeview.get_children():
            self.music_results_treeview.delete(i)
        self.music_results_treeview.insert("", "end", values=("", "Searching, please wait...", "", "", ""))

        # Start the search in a new thread
        search_thread = threading.Thread(
            target=self.perform_music_search,
            args=(song, artist, optional),
            daemon=True
        )
        search_thread.start()

    def perform_music_search(self, song_title, artist, optional_terms):
        """The actual search logic that runs in the background."""
        
        def _perform_single_search(query, limit=10):
            try:
                search = VideosSearch(query, limit=limit)
                return search.result().get('result', [])
            except Exception:
                return []

        # Attempt 1: Full query
        full_query = " ".join(filter(None, [song_title, artist, optional_terms]))
        results = _perform_single_search(full_query)

        # Attempt 2: Fallback to Song + Artist
        if not results:
            song_artist_query = " ".join(filter(None, [song_title, artist]))
            if song_artist_query and song_artist_query != full_query:
                time.sleep(0.5)
                results = _perform_single_search(song_artist_query)

        # Attempt 3: Fallback to just Song Title
        if not results and song_title:
            time.sleep(0.5)
            results = _perform_single_search(song_title)
        
        # Put the final results into the queue for the main thread
        self.music_search_results_queue.put(results)

    def process_music_search_queue(self):
        """Checks the queue for search results and updates the UI."""
        try:
            results = self.music_search_results_queue.get_nowait()
            self.update_music_results_treeview(results)
        except queue.Empty:
            pass # No results yet, do nothing
        finally:
            # Check again after 100ms
            self.after(100, self.process_music_search_queue)

    def update_music_results_treeview(self, video_list):
        """Clears the treeview and populates it with new results."""
        # Clear the "Searching..." message or any old results
        for i in self.music_results_treeview.get_children():
            self.music_results_treeview.delete(i)

        if not video_list:
            self.music_results_treeview.insert("", "end", values=("", "No results found.", "", "", ""))
            return
            
        # Insert new results into the table
        for i, video in enumerate(video_list, 1):
            values = (
                i,
                video.get('title', 'N/A'),
                video.get('channel', {}).get('name', 'N/A'),
                video.get('duration', 'N/A'),
                video.get('link', 'N/A')
            )
            self.music_results_treeview.insert("", "end", values=values)

    # --- END OF NEW MUSIC REQUESTS CODE ---


    def setup_neurosync_widgets(self, parent_frame):
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
        subfolder_name = "start_scripts"
        bat_file_name = "start_neurosync_localapi.bat" 
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bat_file_path = os.path.join(script_dir, subfolder_name, bat_file_name)
        try:
            subprocess.Popen(bat_file_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch the script:\n{e}")

    def run_watcher_to_face_script(self):
        subfolder_name = "start_scripts"
        bat_file_name = "start_neurosync_watcher_to_face.bat" 
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bat_file_path = os.path.join(script_dir, subfolder_name, bat_file_name)
        try:
            subprocess.Popen(bat_file_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch the script:\n{e}")

    def run_main_script(self):
        subfolder_name = "start_scripts"
        bat_file_name = "start_mcp.bat" 
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bat_file_path = os.path.join(script_dir, subfolder_name, bat_file_name)
        try:
            subprocess.Popen(bat_file_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch the script:\n{e}")
            
    def run_styletts2_script(self):
        subfolder_name = "start_scripts"
        bat_file_name = "Start_StyleTTS2.bat" 
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bat_file_path = os.path.join(script_dir, subfolder_name, bat_file_name)
        try:
            subprocess.Popen(bat_file_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch the script:\n{e}")
            
    def run_vision_script(self):
        subfolder_name = "start_scripts"
        bat_file_name = "start_vision.bat" 
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bat_file_path = os.path.join(script_dir, subfolder_name, bat_file_name)
        try:
            subprocess.Popen(bat_file_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch the script:\n{e}")

    def _on_right_pane_mousewheel(self, event):
        if event.num == 5 or event.delta < 0:
            self.ini_canvas.yview_scroll(1, "units")
        if event.num == 4 or event.delta > 0:
            self.ini_canvas.yview_scroll(-1, "units")

    def _bind_mousewheel_for_right_pane(self, event):
        self.bind_all("<MouseWheel>", self._on_right_pane_mousewheel)

    def _unbind_mousewheel_for_right_pane(self, event):
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
    
    def open_music_recognition_help(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        help_dir = os.path.join(script_dir, 'help')
        help_file_path = os.path.join(help_dir, 'Music_Recognition_help.txt')
        try:
            if not os.path.exists(help_dir):
                os.makedirs(help_dir)
            if not os.path.exists(help_file_path):
                with open(help_file_path, 'w', encoding='utf-8') as f:
                    f.write("Music Recognition Help\n" + "="*25 + "\n\n" +
                            "This section contains settings for the music recognition feature.\n\n" +
                            "Key Settings:\n" +
                            "-   **enable:** Set to 'true' to activate the feature.\n" +
                            "-   **api_key:** Enter your API key for the recognition service here.\n\n" +
                            "Remember to click 'Save All Settings' after making changes.")
            if hasattr(os, 'startfile'):
                os.startfile(help_file_path)
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.run([opener, help_file_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open the help file:\n{e}")

    def toggle_sensitive_field(self, entry_widget, button_widget):
        if button_widget.cget("text") == "Show":
            real_value = self.sensitive_values.get(entry_widget, "")
            entry_widget.config(show="")
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, real_value)
            button_widget.config(text="Hide")
        else:
            self.sensitive_values[entry_widget] = entry_widget.get()
            entry_widget.config(show="*")
            button_widget.config(text="Show")

    def reload_ini_ui(self):
        for container in [self.scrollable_frame, self.vision_ini_container, self.neurosync_api_scrollable_frame, self.neurosync_main_scrollable_frame]:
            if container:
                for widget in container.winfo_children():
                    widget.destroy()
        self.ini_entries.clear()
        self.sensitive_values.clear()

        success, error_message = self._read_ini_safely()
        if not success:
            if hasattr(self, 'scrollable_frame'):
                ttk.Label(self.scrollable_frame, text=f"Error reading INI file: {error_message}").pack()
            return

        section_container_map = { 'VisionService': self.vision_ini_container, 'NeurosyncLocalAPI': self.neurosync_api_scrollable_frame, 'Neurosync': self.neurosync_main_scrollable_frame, 'Watcher': self.neurosync_main_scrollable_frame, 'LiveLink': self.neurosync_main_scrollable_frame, }
        default_container = self.scrollable_frame
        
        for section in self.config.sections():
            if section == 'Audio': continue
            parent_container = section_container_map.get(section, default_container)
            if not parent_container: continue

            self.ini_entries[section] = {}
            section_frame = ttk.LabelFrame(parent_container, text=section, padding=10)

            if section == "MusicRecognition":
                header_frame = ttk.Frame(section_frame)
                header_frame.pack(fill='x', expand=True)
                help_button = ttk.Button(header_frame, text="Help", command=self.open_music_recognition_help)
                help_button.pack(side="right")

            for key in self.config.options(section):
                if section == 'VisionService' and key in ('camera_index', 'smol_vlm_model_id'): continue
                
                value = self.config.get(section, key)
                row_frame = ttk.Frame(section_frame); row_frame.pack(fill="x", pady=2, padx=2)
                label = ttk.Label(row_frame, text=f"{key}:", width=20); label.pack(side="left", anchor="n", pady=2)
                
                widget = None
                if key in SENSITIVE_KEYS:
                    widget_frame = ttk.Frame(row_frame)
                    widget_frame.pack(side="left", fill="x", expand=True)
                    widget = ttk.Entry(widget_frame, show="*")
                    widget.insert(0, value)
                    widget.pack(side="left", fill="x", expand=True)
                    self.sensitive_values[widget] = value
                    toggle_button = ttk.Button(widget_frame, text="Show", width=5)
                    toggle_button.config(command=lambda w=widget, b=toggle_button: self.toggle_sensitive_field(w, b))
                    toggle_button.pack(side="left", padx=(5,0))
                elif section == DROPDOWN_SECTION and key == DROPDOWN_KEY:
                    widget = ttk.Combobox(row_frame, values=DROPDOWN_OPTIONS, state="readonly")
                    if value in DROPDOWN_OPTIONS: widget.set(value)
                    widget.pack(side="left", fill="x", expand=True)
                elif '\n' in value:
                    widget = tk.Text(row_frame, height=8, wrap="word")
                    widget.insert("1.0", value)
                    widget.pack(side="left", fill="x", expand=True)
                else:
                    widget = ttk.Entry(row_frame)
                    widget.insert(0, value)
                    widget.pack(side="left", fill="x", expand=True)
                
                if widget:
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
                if saved_index in self.camera_combobox['values']: self.camera_combobox.set(saved_index)
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
                value = ""
                if widget in self.sensitive_values:
                    if widget.cget("show") == "":
                        self.sensitive_values[widget] = widget.get()
                    value = self.sensitive_values[widget]
                else:
                    value = widget.get("1.0", tk.END).strip() if isinstance(widget, tk.Text) else widget.get()
                
                settings_to_update[section][key] = value

        settings_to_update['Audio'] = { 'selected_input': self.selected_input_device_var.get(), 'selected_output': self.selected_output_device_var.get() }
        if 'VisionService' not in settings_to_update: settings_to_update['VisionService'] = {}
        settings_to_update['VisionService']['camera_index'] = self.camera_combobox.get() if self.camera_combobox.get() else "None"
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
        with open(INI_FILE_PATH, 'w', encoding='utf-8') as f: f.writelines(new_lines)
        print("Settings successfully saved!")
        self.reload_ini_ui()

    def populate_camera_list(self):
        available_cameras = []
        for i in range(10):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap is not None and cap.isOpened():
                available_cameras.append(str(i))
                cap.release()
        self.camera_combobox['values'] = available_cameras
        if not available_cameras:
            print("No cameras found with DSHOW backend.")

    def start_camera_preview(self):
        if self.vision_thread and self.vision_thread.is_alive(): return
        cam_index_str = self.camera_combobox.get()
        if not cam_index_str: return
        self.stop_vision_thread = False
        self.vision_thread = threading.Thread(target=self._video_capture_loop, args=(int(cam_index_str),), daemon=True)
        self.vision_thread.start()

    def stop_camera_preview(self):
        self.stop_vision_thread = True
        self.video_label.config(image='', text="Preview stopped")
        self.video_label.image = None

    def _video_capture_loop(self, camera_index):
        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            self.video_frame_queue.put(f"Failed to open camera {camera_index}")
            return
        while not self.stop_vision_thread:
            ret, frame = cap.read()
            if not ret: continue
            pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            try: self.video_frame_queue.put_nowait(pil_img)
            except queue.Full: pass
        cap.release()

    def process_video_queue(self):
        try:
            item = self.video_frame_queue.get_nowait()
            if isinstance(item, str):
                self.video_label.config(image='', text=item, fg="red")
                self.video_label.image = None
            else:
                label_w, label_h = self.video_label.winfo_width(), self.video_label.winfo_height()
                if label_w > 1 and label_h > 1:
                    item.thumbnail((label_w, label_h), Image.Resampling.LANCZOS)
                    photo_image = ImageTk.PhotoImage(image=item)
                    self.video_label.config(image=photo_image, text="")
                    self.video_label.image = photo_image
        except queue.Empty: pass
        self.after(30, self.process_video_queue)

    def on_closing(self):
        self.stop_vision_thread = True
        self.is_testing_output = False
        if self.input_stream: self.input_stream.close()
        if self.output_stream: self.output_stream.close()
        self.destroy()

    def populate_device_lists(self):
        try:
            devices = sd.query_devices()
            self.input_listbox.delete(0, tk.END)
            self.output_listbox.delete(0, tk.END)
            for i, d in enumerate(devices):
                if not d['name'].strip().endswith("Voic"):
                    if d['max_input_channels'] > 0: self.input_listbox.insert(tk.END, f"[{i}] {d['name']}")
                    if d['max_output_channels'] > 0: self.output_listbox.insert(tk.END, f"[{i}] {d['name']}")
        except Exception as e: print(f"Error querying devices: {e}")

    def setup_input_widgets(self, parent_frame):
        device_frame = ttk.Frame(parent_frame); device_frame.pack(pady=5, fill="x")
        ttk.Label(device_frame, text="Selected Input Device:").pack(side="left")
        self.selected_input_device_var = tk.StringVar(value="None")
        ttk.Entry(device_frame, textvariable=self.selected_input_device_var, state="readonly").pack(side="left", fill="x", expand=True, padx=5)
        list_frame = ttk.Frame(parent_frame); list_frame.pack(pady=5, fill="both", expand=True)
        ttk.Label(list_frame, text="Mic device list (Double-click to select):").pack(anchor="w")
        self.input_listbox = tk.Listbox(list_frame, exportselection=False); self.input_listbox.pack(side="left", fill="both", expand=True)
        self.input_listbox.bind("<Double-Button-1>", self.on_input_device_select)
        ttk.Label(parent_frame, text="Input VU Meter:").pack(anchor="w", pady=(5, 0))
        self.input_vu_meter_canvas = tk.Canvas(parent_frame, height=30, bg="lightgrey", relief="sunken"); self.input_vu_meter_canvas.pack(pady=5, fill="x")

    def setup_output_widgets(self, parent_frame):
        device_frame = ttk.Frame(parent_frame); device_frame.pack(pady=5, fill="x")
        ttk.Label(device_frame, text="Selected Output Device:").pack(side="left")
        self.selected_output_device_var = tk.StringVar(value="None")
        ttk.Entry(device_frame, textvariable=self.selected_output_device_var, state="readonly").pack(side="left", fill="x", expand=True, padx=5)
        list_frame = ttk.Frame(parent_frame); list_frame.pack(pady=5, fill="both", expand=True)
        ttk.Label(list_frame, text="Output device list (Double-click to select):").pack(anchor="w")
        self.output_listbox = tk.Listbox(list_frame, exportselection=False); self.output_listbox.pack(side="left", fill="both", expand=True)
        self.output_listbox.bind("<Double-Button-1>", self.on_output_device_select)
        self.test_output_button = ttk.Button(list_frame, text="Test", command=self.toggle_output_test, width=10); self.test_output_button.pack(side="left", padx=5, anchor="n")
        ttk.Label(parent_frame, text="Output Test VU Meter:").pack(anchor="w", pady=(5, 0))
        self.output_vu_meter_canvas = tk.Canvas(parent_frame, height=30, bg="lightgrey", relief="sunken"); self.output_vu_meter_canvas.pack(pady=5, fill="x")

    def on_input_device_select(self, event):
        sel = self.input_listbox.curselection()
        if not sel: return
        self.selected_input_device_var.set(self.input_listbox.get(sel[0]))
        self.start_input_stream(int(self.input_listbox.get(sel[0]).split(']')[0][1:]))

    def on_output_device_select(self, event):
        sel = self.output_listbox.curselection()
        if not sel: return
        self.selected_output_device_var.set(self.output_listbox.get(sel[0]))

    def toggle_output_test(self):
        if self.is_testing_output: self.stop_output_test()
        else:
            sel_text = self.selected_output_device_var.get()
            if sel_text == "None" or "[" not in sel_text: return
            self.start_output_test(int(sel_text.split(']')[0][1:]))

    def start_input_stream(self, device_id):
        if self.input_stream: self.input_stream.close()
        try:
            samplerate = sd.query_devices(device_id, 'input')['default_samplerate']
            self.input_stream = sd.InputStream(device=device_id, channels=1, samplerate=samplerate, callback=self.input_audio_callback)
            self.input_stream.start()
        except Exception as e: print(f"Error starting input stream: {e}")

    def input_audio_callback(self, indata, frames, time, status):
        rms = np.sqrt(np.mean(indata**2)); current_db = 20 * math.log10(rms) if rms > 0 else MIN_DB
        self.input_audio_queue.put(current_db)

    def start_output_test(self, device_id):
        self.is_testing_output = True; self.test_output_button.config(text="Stop")
        try:
            samplerate = sd.query_devices(device_id, 'output')['default_samplerate']
            self.output_stream = sd.OutputStream(device=device_id, channels=1, samplerate=samplerate, callback=self.output_audio_callback)
            self.output_stream.start()
        except Exception as e: self.stop_output_test()

    def stop_output_test(self):
        if self.output_stream: self.output_stream.close()
        self.output_stream = None; self.is_testing_output = False
        self.test_output_button.config(text="Test")
        self.output_smoothed_db = MIN_DB; self.output_peak_db = MIN_DB

    def output_audio_callback(self, outdata, frames, time, status):
        t = (self.output_start_idx + np.arange(frames)) / self.output_stream.samplerate
        outdata[:] = 0.5 * np.sin(2 * np.pi * TEST_TONE_FREQUENCY * t).reshape(-1, 1)
        self.output_start_idx += frames
        rms = np.sqrt(np.mean(outdata[:]**2)); current_db = 20 * math.log10(rms) if rms > 0 else MIN_DB
        self.output_audio_queue.put(current_db)

    def process_audio_queues(self):
        try:
            current_db = self.input_audio_queue.get_nowait()
            self.input_smoothed_db = (SMOOTHING_FACTOR * self.input_smoothed_db) + ((1 - SMOOTHING_FACTOR) * current_db)
            if self.input_smoothed_db > self.input_peak_db: self.input_peak_db, self.input_peak_hold_time = self.input_smoothed_db, time.time()
        except queue.Empty: pass
        if time.time() - self.input_peak_hold_time > PEAK_HOLD_DURATION: self.input_peak_db = max(self.input_smoothed_db, self.input_peak_db - 2)
        
        try:
            current_db = self.output_audio_queue.get_nowait()
            self.output_smoothed_db = (SMOOTHING_FACTOR * self.output_smoothed_db) + ((1 - SMOOTHING_FACTOR) * current_db)
            if self.output_smoothed_db > self.output_peak_db: self.output_peak_db, self.output_peak_hold_time = self.output_smoothed_db, time.time()
        except queue.Empty: pass
        
        if self.is_testing_output:
            if time.time() - self.output_peak_hold_time > PEAK_HOLD_DURATION: self.output_peak_db = max(self.output_smoothed_db, self.output_peak_db - 2)
        else:
            self.output_smoothed_db = max(MIN_DB, self.output_smoothed_db - 3); self.output_peak_db = max(self.output_smoothed_db, self.output_peak_db - 3)
        
        self.update_vu_meter_canvas(self.input_vu_meter_canvas, self.input_smoothed_db, self.input_peak_db)
        self.update_vu_meter_canvas(self.output_vu_meter_canvas, self.output_smoothed_db, self.output_peak_db)
        self.after(50, self.process_audio_queues)

    def update_vu_meter_canvas(self, canvas, smoothed_db, peak_db):
        width, height = canvas.winfo_width(), canvas.winfo_height()
        if width <= 1: return
        canvas.delete("all")
        bar_len = int(((max(MIN_DB, min(smoothed_db, MAX_DB)) - MIN_DB) / (MAX_DB - MIN_DB)) * width)
        green_w, yellow_w = int(width * 0.7), int(width * 0.9)
        if bar_len > 0: canvas.create_rectangle(0, 0, min(bar_len, green_w), height, fill="#4CAF50", width=0)
        if bar_len > green_w: canvas.create_rectangle(green_w, 0, min(bar_len, yellow_w), height, fill="#FFC107", width=0)
        if bar_len > yellow_w: canvas.create_rectangle(yellow_w, 0, bar_len, height, fill="#F44336", width=0)
        peak_pos = int(((max(MIN_DB, min(peak_db, MAX_DB)) - MIN_DB) / (MAX_DB - MIN_DB)) * width)
        if peak_pos > 1: canvas.create_line(peak_pos, 0, peak_pos, height, fill="black", width=2)
        canvas.create_text(width - 10, height / 2, text=f"{smoothed_db:.2f} dB", anchor="e")

if __name__ == "__main__":
    if not os.path.exists(INI_FILE_PATH):
        with open(INI_FILE_PATH, "w", encoding='utf-8') as f:
            f.write("[General]\n"
                    "setting1 = value1\n"
                    "session_id = replace_with_real_session_id\n\n"
                    "[Audio]\n"
                    "selected_input = None\n"
                    "selected_output = None\n\n"
                    "[MusicRecognition]\n"
                    "enable = true\n"
                    "api_key = your_api_key_here\n\n"
                    "[VisionService]\n"
                    "camera_index = None\n"
                    "smol_vlm_model_id = HuggingFaceTB/SmolVLM-500M-Instruct\n\n"
                    "[Watcher]\n"
                    "target_file_path = C:/path/to/server_output.wav\n\n"
                    "[Neurosync]\n"
                    "neurosync_local_url = http://127.0.0.1:9000/audio_to_blendshapes\n\n"
                    "[NeurosyncLocalAPI]\n"
                    "host = 127.0.0.1\n"
                    "port = 9000\n\n"
                    "[LiveLink]\n"
                    "ip = 192.168.1.101\n"
                    "port = 11111\n\n"
                    f"[{DROPDOWN_SECTION}]\n"
                    f"{DROPDOWN_KEY} = gemini\n")
            
    app = AudioApp()
    app.mainloop()