import webview
import logging
import os
import socket
import time
import threading
import uvicorn
import urllib.request
from backend.api import app

log_path = os.path.expanduser("~/LocationChanger.log")
logging.basicConfig(filename=log_path, level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s: %(message)s')
logging.info("V2 App starting...")

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def run_server(port):
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")

if __name__ == "__main__":
    try:
        port = find_free_port()
        logging.info(f"Binding ASGI server to port {port}")
        
        t = threading.Thread(target=run_server, args=(port,), daemon=True)
        t.start()
        
        for _ in range(20):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/api/status", timeout=0.5)
                break
            except Exception:
                time.sleep(0.2)
        
        logging.info("Starting webview...")
        window = webview.create_window('iOS Location Changer (V2)', f'http://127.0.0.1:{port}', width=1000, height=700, transparent=True, vibrancy=True)
        webview.start()
        
        logging.info("Webview closed normally.")
    except Exception as e:
        logging.exception(f"Fatal error in main: {e}")
