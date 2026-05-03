import os  
import threading  
import subprocess  
import sys  
from flask import Flask, request, jsonify  
from flask_cors import CORS  
from playwright.sync_api import sync_playwright

app = Flask(__name__)  
CORS(app)

# --- BRUTE FORCE INSTALLER ---  
def ensure_browser():  
    print("[SINC-SYNC] Checking for browser binaries...")  
    try:  
        # This force-installs chromium directly into the container at runtime  
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)  
        print("[SINC-SYNC] Browser binaries successfully forced into existence.")  
    except Exception as e:  
        print(f"[SINC-SYNC] MANUAL INSTALL FAILED: {e}")

# Run the installer immediately on script load  
ensure_browser()  
# -----------------------------

browser_state = {  
    "status": "IDLE",  
    "last_command": None,  
    "session_active": False  
}

def run_browser_task(command):  
    try:  
        with sync_playwright() as p:  
            browser = p.chromium.launch(headless=True)  
            page = browser.new_page()  
            if "screenshot" in command:  
                page.goto("https://example.com")  
                page.screenshot(path="proof_of_life.png")  
                browser.close()  
                return "SUCCESS: Screenshot saved as proof_of_life.png"  
            browser.close()  
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
    result = run_browser_task(cmd)  
    browser_state["status"] = "IDLE"  
    return jsonify({"result": result, "cmd": cmd, "status": "COMPLETED"}), 200

def run_mpc():  
    port = int(os.environ.get("PORT", 8080))  
    print(f"[SINC-SYNC] BINDING TO PORT: {port}...")  
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def start_mpc_bridge():  
    mpc_thread = threading.Thread(target=run_mpc, daemon=True)  
    mpc_thread.start()  
    print("[SINC-SYNC] MPC Bridge successfully injected and listening...")  
