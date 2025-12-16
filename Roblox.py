import threading
from keyboard_handler import stop_key_listener
from automation import run_automation

if __name__ == "__main__":
    listener_thread = threading.Thread(target=stop_key_listener, daemon=True)
    listener_thread.start()
    run_automation()