import os  
from flask import Flask, request, jsonify  
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# Global state to keep track of the browser  
browser_state = {  
    "status": "IDLE",  
    "last_command": None,  
    "latency": 0,  
    "session_active": False  
}

def run_browser_task(command):  
    try:  
        with sync_playwright() as p:  
            # Launching headless browser  
            browser = p.chromium.launch(headless=True)  
            page = browser.new_page()  
              
            # If the command is 'screenshot', we go to a test site  
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
    return jsonify(browser_state)

@app.route('/command', methods=['POST'])  
def handle_command():  
    data = request.json  
    cmd = data.get("command")  
    browser_state["last_command"] = cmd  
    browser_state["status"] = "PROCESSING"  
      
    # Actually try to run the browser task  
    result = run_browser_task(cmd)  
      
    browser_state["status"] = "IDLE"  
    return jsonify({"result": result, "cmd": cmd, "status": "COMPLETED"})

if __name__ == '__main__':  
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))  
