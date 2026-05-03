import os  
import threading  
from flask import Flask, request, jsonify  
from flask_cors import CORS

app = Flask(__name__)  
CORS(app)

# GLOBAL STATE FOR THE GHOST  
# This acts as the shared memory between the MPC bridge and the Ghost kernel  
ghost_state = {  
    "status": "IDLE",  
    "session_active": False,  
    "last_command": None,  
    "latency": 0  
}

@app.route('/status', methods=['GET'])  
def get_status():  
    """Heartbeat endpoint to verify the bridge is alive."""  
    return jsonify(ghost_state), 200

@app.route('/command', methods=['POST'])  
def execute_command():  
    """Command injection endpoint for remote control."""  
    try:  
        data = request.json  
        if not data:  
            return jsonify({"error": "No JSON payload provided"}), 400  
              
        cmd = data.get("command")  
        if not cmd:  
            return jsonify({"error": "No 'command' field found in request"}), 400

        ghost_state["last_command"] = cmd  
        ghost_state["status"] = "EXECUTING"

        # This print is our primary debug line in the Railway logs  
        print(f"[MPC_CORE] RECEIVED COMMAND: {cmd}")

        # Return immediate confirmation to the sender  
        return jsonify({  
            "result": "Command received by Sovereign Kernel",   
            "cmd": cmd,   
            "status": "QUEUED"  
        }), 200  
          
    except Exception as e:  
        print(f"[MPC_ERROR] Execution failed: {e}")  
        return jsonify({"error": str(e)}), 500

def run_mpc():  
    """The internal Flask engine."""  
    # Railway injects the port via environment variable.   
    # We default to 8080 but the 'PORT' var MUST be set in Railway Settings.  
    port = int(os.environ.get("PORT", 8080))  
    print(f"[SINC-SYNC] ATTEMPTING BIND TO PORT: {port}...")  
      
    try:  
        # host='0.0.0.0' is mandatory for the container to be accessible from the web  
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)  
    except Exception as e:  
        print(f"[CRITICAL_ERROR] BIND FAILED: {e}")

def start_mpc_bridge():  
    """Thread-safe launcher for the MPC server."""  
    mpc_thread = threading.Thread(target=run_mpc, daemon=True)  
    mpc_thread.start()  
    print("[SINC-SYNC] MPC Bridge successfully injected and listening...")  
