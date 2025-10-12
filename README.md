# Unified Multimodal AI Control System

This project is a sophisticated AI system designed around a central "brain" called the **Master Control Program (MCP)**. It features a flexible, multimodal architecture, allowing it to process and understand text, images, and audio. This design enables it to operate in a unified mode—processing multiple data types at once—or in specialized pipelines that handle each type of input separately.

The system is engineered to be highly interactive, not only conversing with users but also interfacing with external platforms and game engines to create a dynamic and immersive experience.

## Core Components

At its heart, the system is comprised of several key scripts that work in concert:

### Master Control Program (`mcp_v1b.py`)
This is the central hub of the entire system. It receives inputs from all other components, decides how to process them, and orchestrates the AI's behavior.
- **Unified & Pipelined Architecture:** Supports various LLMs and modes, including a unified multimodal mode for advanced models that can understand images and text simultaneously.
- **Long-Term Memory:** Maintains the system's memory using a robust vector database (ChromaDB).
- **External Communication:** Sends commands to Unreal Engine via OSC and broadcasts messages to social platforms.

### Vision Service (`vision.py`)
This script acts as the eyes of the system, capturing video input from a physical **webcam** or a virtual **NDI (Network Device Interface) stream**. This flexibility allows for both simple local setups and more complex production environments.
- **Dual-Mode Capability:** It can provide raw image data for direct analysis by the MCP or use a local Vision Language Model (VLM) to generate text descriptions of what it sees.

### Audio Client (`listen.py`)
This is the ears of the system. It continuously listens for spoken commands through a microphone.
- **Speech-to-Text:** Uses a local Whisper model to transcribe any speech it hears into text and sends it to the MCP for interpretation and action.

### Facial Animation (`watcher_to_face.py` and `neurosync_local_api.py`)
These scripts give the system a face.
- `watcher_to_face.py`: Monitors for audio output from the TTS engine and triggers corresponding facial animations.
- `neurosync_local_api.py`: Provides an API to convert audio signals into the detailed facial movements (blendshapes) needed for realistic animation.

## External Integrations

A key feature of this system is its ability to connect with other services and applications:

### Social Stream Ninja
For text-based chat, the system integrates with Social Stream Ninja. This allows the MCP to receive chat messages from users on various social platforms (like Twitch, YouTube, etc.) and send its responses back to be broadcast to those audiences. This turns the AI into an interactive social presence.

### Unreal Engine (via OSC)
The system communicates with Unreal Engine using the **Open Sound Control (OSC)** protocol. This allows the MCP to send commands directly into the game engine to control an avatar, trigger events, change the environment, or interact with objects, making the AI a true agent within a virtual world.

## How It Works

The system is designed to be highly modular. A typical interaction follows this workflow:

1.  **Input:** An interaction is initiated. This can happen in two primary ways:
    *   A user speaks a command, which is picked up by the **Audio Client**, transcribed, and sent to the MCP.
    *   A user types a message in a chat connected to **Social Stream Ninja**, which forwards the text to the MCP.

2.  **Processing:** The MCP receives the text. If the command requires visual information (e.g., "what do you see?"), it requests data from the **Vision Service**, which is capturing a feed from a webcam or NDI source. The MCP then uses its language model to interpret the user's request in the full context of the conversation and any visual data.

3.  **Action & Response:** The MCP formulates a response and takes action.
    *   **Spoken Response:** The text response is sent to a text-to-speech (TTS) engine, generating an audio file.
    *   **Facial Animation:** The **Facial Animation** scripts detect this audio file and use the `neurosync_local_api.py` to generate synchronized facial movements for a virtual character.
    *   **Game Engine Control:** If the command was an action (e.g., "go to the kitchen"), the MCP sends a command via **OSC to Unreal Engine** to move the character.
    *   **Chat Broadcast:** The text response is also sent back through **Social Stream Ninja** to be displayed in the chat.

This unified and pipelined approach allows for a rich, interactive experience where the AI can not only understand and respond to users across multiple platforms but also perceive and react to its visual environment, all while presenting a dynamic and expressive virtual persona in Unreal Engine.
