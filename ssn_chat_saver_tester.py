from flask import Flask, request, jsonify
import json
import aiofiles
import os

app = Flask(__name__)

LOG_FILE = 'chat_log.jsonl'

@app.route('/chat', methods=['POST'])
async def receive_chat():
    try:
        # In Flask 2.0+, request.json still works inside async routes
        data = request.json

        if data:
            print(f"New Message: {data}")

            # 3. Asynchronous File Writing
            # We use 'async with' and 'aiofiles.open' so it doesn't block the server
            async with aiofiles.open(LOG_FILE, mode='a', encoding='utf-8') as f:
                await f.write(json.dumps(data, ensure_ascii=False) + "\n")
            
            return jsonify({"status": "success", "message": "Logged"}), 200
        else:
            return jsonify({"status": "error", "message": "No JSON data"}), 400

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print(f"Async Server listening at http://127.0.0.1:5000/chat")
    # Flask 2.0's built-in server handles async routes automatically
    app.run(host='127.0.0.1', port=5000, debug=True)