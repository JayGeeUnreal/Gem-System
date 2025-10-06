1. Purpose
The Master Control Program (MCP) is the central "brain" of the entire AI system. It acts as an intelligent orchestrator, receiving input from various sources (like chat, audio, or a vision system), deciding how to process that input, and then dispatching tasks to the appropriate services.
Its primary goal is to understand user requests, enrich them with contextual information (like what the camera sees), get a meaningful response from a powerful Large Language Model (LLM), and then broadcast that response to output channels like a Text-to-Speech (TTS) engine or a social media live stream.
2. Features
    • Unified Server Architecture: Provides a single, centralized Flask web server to handle requests from all other scripts.
    • Multi-LLM Support: Can be configured to use either Google's Gemini or a local Ollama model as its core reasoning engine.
    • Wake Word Detection: Ignores all input unless it begins with a configured "wake word" (e.g., "computer," "assistant"), preventing it from responding to unintended chatter.
    • Intelligent Vision Integration:
        ◦ Uses a cached "memory" of the last thing it saw to answer questions without needing a new scan every time.
        ◦ Automatically requests a fresh scan from the vision.py service when it detects vision-related keywords (e.g., "look," "see," "what is that").
    • Intent Recognition: Differentiates between a general question and a direct command to provide better-formatted prompts to the LLM.
    • External Service Integration:
        ◦ Vision Service: Can command the vision script to perform a visual scan.
        ◦ StyleTTS: Sends final responses to a TTS server to be spoken aloud.
        ◦ Social Stream Ninja: Pushes final responses to a live streaming overlay.
    • Response Management: Can truncate long LLM responses to a configured maximum length to keep them concise.
3. How it Works
The MCP operates as a continuous web service. The typical workflow for a request is as follows:
    1. An external service (e.g., an audio transcriber) sends a user's text to one of MCP's API endpoints (like /audio).
    2. The request is routed to the central process_task() function.
    3. The function first checks if the user's text starts with a valid wake word. If not, it ignores the request.
    4. If a wake word is present, it determines the necessary visual context. If the request came from the vision service, it uses the fresh context provided. If not, it checks for trigger words; if found, it calls the vision.py service for a new scan. Otherwise, it uses its cached visual memory.
    5. It constructs a detailed prompt for the LLM, combining the user's text and the visual context.
    6. The prompt is sent to the configured LLM (Gemini or Ollama).
    7. The LLM's raw response is received, cleaned up, and truncated if necessary.
    8. This final, polished response is then sent to the StyleTTS service (to be spoken) and the Social Stream Ninja service (to be displayed).
    9. A confirmation response is sent back to the service that made the original request.
4. Setup & Installation
    • Dependencies: You must have the required Python libraries installed. You can install them all with the following command:
      codeBash
    • !! OBS USE PYTHON 3.10 THIS IS REQUIRED FOR FLASH-ATTN2 !!
    • You can compile your own wheel but I use the wheel from this link
    • https://github.com/sunsetcoder/flash-attention-windows
    • cd C:\Users\jorge\Documents\AI\gem-system
    • conda create --name mcp_env_1 python=3.10 -y
    • conda activate mcp_env_1
    • pip install Flask Flask-Cors google-generativeai requests 
    • pip install opencv-python Pillow 
    • # torch torchvision This depends on your cuda version 
    • # Use nvcc –version to get the cuda version you have installed.
    • # Then go to https://pytorch.org/get-started/locally/ to get the command to run.
    • # For my set up the install command is
    • pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu128
    • pip3 install  torchaudio
    • pip3  install transformers
    • pip3  install accelerate
    • pip install sounddevice webrtcvad scipy 
    • pip install python-osc
    • pip install opencv-python
    • pip install ninja 
    • Configuration (mcp_settings.ini): This file is critical for the MCP's operation. It must be in the same directory as the script. Below is a description of each setting:
        ◦ [MCP]
            ▪ llm_choice: The core LLM to use. Must be either gemini or ollama.
            ▪ host: The IP address for the server to run on (e.g., 127.0.0.1 for local only, 0.0.0.0 for network access).
            ▪ port: The port for the server (e.g., 5000).
        ◦ [Assistant]
            ▪ max_response_length: The maximum number of characters for the final response. Set to 0 to disable truncation.
            ▪ wake_words: A comma-separated list of words that the assistant will respond to (e.g., computer, assistant, jarvis).
            ▪ command_verbs: A comma-separated list of words that indicate the user is giving a command (e.g., go to, open, start).
        ◦ [VisionService]
            ▪ scan_url: The full URL to the vision service's scan endpoint (e.g., http://127.0.0.1:5001/scan).
            ▪ vision_trigger_words: Comma-separated words that trigger a new vision scan (e.g., look, see, what do you see, analyze).
        ◦ [SocialStream]
            ▪ enabled: Set to true or false to enable/disable integration.
            ▪ session_id, target_platform, api_url: Settings specific to your Social Stream Ninja setup.
        ◦ [StyleTTS]
            ▪ enabled: Set to true or false to enable/disable integration.
            ▪ tts_url: The URL for your StyleTTS server's endpoint.
        ◦ [Gemini]
            ▪ api_key: Required if llm_choice is gemini. Your Google AI Studio API key.
            ▪ model: The specific Gemini model to use (e.g., gemini-1.5-flash).
        ◦ [Ollama]
            ▪ model: Required if llm_choice is ollama. The name of the Ollama model (e.g., llama3:instruct).
            ▪ api_url: The URL to the Ollama chat API endpoint (e.g., http://localhost:11434/api/chat).
5. Usage
    • Running the Script:
        1. Ensure your mcp_settings.ini file is correctly configured.
        2. Run the script from your terminal:
           codeBash
           Cd …….\gem-system
        3. conda activate mcp_env_1
        4. python mcp.py
        5. The server will start and print the address it is listening on.
    • API Endpoints: The MCP is controlled by sending HTTP requests to its endpoints.
        1. /chat (POST, PUT)
            ▪ Purpose: To process input from a text-based chat interface.
            ▪ Payload: {"chatmessage": "your message here"}
            ▪ Returns: {"status": "ok"}
        2. /vision (POST)
            ▪ Purpose: To process input from the vision.py client, which includes fresh visual context.
            ▪ Payload: {"text": "user's command", "vision_context": "description from VLM"}
            ▪ Returns: {"response": "the final answer from the LLM"}
        3. /audio (POST)
            ▪ Purpose: To process transcribed text from an audio input source.
            ▪ Payload: {"text": "transcribed user speech"}
            ▪ Returns: {"response": "the final answer from the LLM"}

        4. /update_vision (POST)
            ▪ Purpose: Allows an external service (like vision.py) to update the MCP's visual memory without asking a question.
            ▪ Payload: {"vision_context": "new visual description"}
            ▪ Returns: {"status": "vision context updated"}
6. Code Breakdown
    • load_config(): Safely loads all settings from the .ini file and exits if any critical setting is missing.
    • ask_llm(): An abstraction function that routes the prompt to either the Gemini or Ollama API based on the configuration.
    • send_to_...() functions: A set of helper functions (send_to_social_stream, send_to_tts) that handle the logic of sending the final response to output services.
    • process_task(): This is the most important function. It contains the core decision-making logic: wake word check, vision context handling, and prompt construction.
    • Flask @app.route functions: These define the API endpoints and serve as the entry points for all external communication, each calling process_task to do the heavy lifting.
