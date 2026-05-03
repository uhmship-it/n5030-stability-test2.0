import os  
import threading  
import requests  
from flask import Flask, request, jsonify  
from flask_cors import CORS

app = Flask(__name__)  
CORS(app)

browser_state = {"status": "IDLE", "last_command": None}

def run_ghost_task(command):  
    try:  
        if "screenshot" in command:  
            print("[SINC-SYNC] Fetching page content...")  
            response = requests.get("https://example.com", timeout=10)  
            with open("proof_of_life.txt", "w", encoding="utf-8") as f:  
                f.write(response.text)  
            return "SUCCESS: Ghost-Lite captured the page content!"  
        return f"Executed: {command}"  
    except Exception as e:  
        return f"CRITICAL ERROR: {str(e)}"

@app.route('/status', methods=['GET'])  
def get_status():  
    return jsonify(browser_state), 200

@app.route('/command', methods=['POST'])  
def handle_command():  
    data = request.json  
    cmd = data.get("command")  
    browser_state["last_command"] = cmd  
    browser_state["status"] = "PROCESSING"  
    result = run_ghost_task(cmd)  
    browser_state["status"] = "IDLE"  
    return jsonify({"result": result, "cmd": cmd, "status": "COMPLETED"}), 200

def run_mpc():  
    port = int(os.environ.get("PORT", 8080))  
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == "__main__":  
    # Run in a thread to prevent blocking  
    t = threading.Thread(target=run_mpc, daemon=True)  
    t.start()  
    print("[SINC-SYNC] MPC Bridge (Lite) is NOW LIVE.")  
    # Keep main thread alive  
    import time  
    while True:  
        time.sleep(1)  
