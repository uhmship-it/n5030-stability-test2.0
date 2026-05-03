import os  
import threading  
import subprocess  
import sys  
import time  
from flask import Flask, request, jsonify  
from flask_cors import CORS  
from playwright.sync_api import sync_playwright

app = Flask(__name__)  
CORS(app)

def ensure_browser():  
    print("[SINC-SYNC] Checking for browser binaries...")  
    try:  
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)  
        print("[SINC-SYNC] Browser binaries confirmed.")  
    except Exception as e:  
        print(f"[SINC-SYNC] INSTALL ERROR: {e}")

ensure_browser()

browser_state = {"status": "IDLE", "last_command": None, "session_active": False}

def run_browser_task(command):  
    try:  
        with sync_playwright() as p:  
            # Added args to prevent crashes in container environments  
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])  
            context = browser.new_context()  
            page = context.new_page()  
              
            if "screenshot" in command:  
                print("[SINC-SYNC] Attempting to navigate...")  
                page.goto("https://example.com", wait_until="networkidle")  
                time.sleep(2) # Give it a moment to settle  
                page.screenshot(path="proof_of_life.png")  
                print("[SINC-SYNC] Screenshot captured successfully.")  
                browser.close()  
                return "SUCCESS: Ghost has seen the world. Screenshot saved."  
              
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
    print("[SINC-SYNC] MPC Bridge successfully injected.")  
