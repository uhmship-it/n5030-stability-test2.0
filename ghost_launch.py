from mpc_core import start_mpc_bridge
start_mpc_bridge()
import zipfile
import os
from playwright.sync_api import sync_playwright

def start():
    try:
        print("Searching for identity zip...")
        zip_filename = 'sovereign_identity.zip'

        if not os.path.exists(zip_filename):
            print(f"ERROR: {zip_filename} not found!")
            return

        print("Unzipping identity...")
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            zip_ref.extractall('/tmp/identity')

        with sync_playwright() as p:
            print("Launching browser...")
            browser = p.chromium.launch_persistent_context(
                user_data_dir='/tmp/identity',
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            page = browser.new_page()
            page.goto("https://grok.com")

            if "Connect your X account" not in page.content():
                print("SUCCESS: You are logged into Grok!")
            else:
                print("FAIL: Session rejected.")
            browser.close()

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")

if __name__ == "__main__":
    start()
