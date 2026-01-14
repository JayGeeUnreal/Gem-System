from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# File to save chats to
LOG_FILE = 'chat_log.jsonl'

@app.route('/chat', methods=['POST'])
def receive_chat():
    try:
        # Social Stream Ninja usually sends data as JSON
        data = request.json

        if data:
            # 1. Print to console (so you know it's working)
            print(f"New Message: {data}")

            # 2. Append to file (JSON Lines format)
            # We use 'a' for append mode. 
            # ensure_ascii=False ensures emojis are saved correctly.
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
            
            return jsonify({"status": "success", "message": "Logged"}), 200
        else:
            print("Received request but no JSON data found.")
            return jsonify({"status": "error", "message": "No JSON data"}), 400

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Running on 0.0.0.0 allows access from local network if needed, 
    # but 127.0.0.1 is fine for just this machine.
    print(f"Server listening at http://127.0.0.1:5000/chat")
    app.run(host='127.0.0.1', port=5000, debug=True)