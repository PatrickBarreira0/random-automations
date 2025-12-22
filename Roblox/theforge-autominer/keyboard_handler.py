import keyboard
from config import STOP_KEY

running = True

def stop_key_listener():
    global running
    print(f"\n[INFO] Press '{STOP_KEY}' at any time to stop.")
    keyboard.wait(STOP_KEY)
    running = False
    print(f"\n[INFO] Stop key '{STOP_KEY}' pressed. The script will halt after the current action.")

def is_running():
    return running

def set_running(value):
    global running
    running = value


