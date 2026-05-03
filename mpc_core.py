import os
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# GLOBAL STATE FOR THE GHOST
ghost_state = {
    "status": "IDLE",
    "session_active": False,
    "last_command": None,
    "latency": 0
}

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(ghost_state), 200

@app.route('/command', methods=['POST'])
def execute_command():
    data = request.json
    cmd = data.get("command")
    
    ghost_state["last_command"] = cmd
    ghost_state["status"] = "EXECUTING"
    
    # This is the bridge to ghost_launch.py
    print(f"[MPC_CORE] RECEIVED COMMAND: {cmd}")
    
    # Logic here will be linked to the Playwright instance in the main thread
    return jsonify({"result": "Command received by Sovereign Kernel", "cmd": cmd}), 200

def run_mpc():
    port = int(os.environ.get("PORT", 8080))
    # use_reloader must be False to prevent double-injection in threading
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def start_mpc_bridge():
    mpc_thread = threading.Thread(target=run_mpc, daemon=True)
    mpc_thread.start()
    print("[SINC-SYNC] MPC Bridge successfully injected and listening...")
