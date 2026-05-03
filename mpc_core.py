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
    try:  
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)  
    except:  
        pass

ensure_browser()

browser_state = {"status": "IDLE", "last_command": None}

def run_browser_task(command):  
    try:  
        with sync_playwright() as p:  
            # MINIMALIST LAUNCH: No extensions, no GPU, no sandbox, minimal memory  
            browser = p.chromium.launch(  
                headless=True,  
                args=[  
                    "--no-sandbox",  
                    "--disable-setuid-sandbox",  
                    "--disable-dev-shm-usage",  
                    "--disable-gpu",  
                    "--single-process",  
                    "--disable-extensions",  
                    "--disable-component-update"  
                ]  
            )  
            # Use a tiny viewport to save RAM  
            context = browser.new_context(viewport={'width': 800, 'height': 600})  
            page = context.new_page()

            if "screenshot" in command:  
                # Use 'commit' wait instead of 'networkidle' to save memory/time  
                page.goto("https://example.com", wait_until="commit", timeout=30000)  
                page.screenshot(path="proof_of_life.png")  
                browser.close()  
                return "SUCCESS: SKINNY GHOST SAW THE WORLD."

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
    browser_state["status"] = "PROCESSING"  
    result = run_browser_task(cmd)  
    browser_state["status"] = "IDLE"  
    return jsonify({"result": result, "cmd": cmd, "status": "COMPLETED"}), 200

def run_mpc():  
    port = int(os.environ.get("PORT", 8080))  
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def start_mpc_bridge():  
    mpc_thread = threading.Thread(target=run_mpc, daemon=True)  
    mpc_thread.start()  
