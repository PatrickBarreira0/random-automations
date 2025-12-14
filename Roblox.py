import pyautogui
import autoit
import cv2
import numpy as np
import time
import random
import threading
import keyboard

CONFIDENCE_LEVEL = 0.8
STOP_KEY = 'k'
running = True

def stop_key_listener():
    global running
    print(f"\n[INFO] Press '{STOP_KEY}' at any time to stop.")
    keyboard.wait(STOP_KEY)
    running = False
    print(f"\n[INFO] Stop key '{STOP_KEY}' pressed. The script will halt after the current action.")

def find_and_click(template_image, confidence=CONFIDENCE_LEVEL, timeout=5):

    start_time = time.time()
    template_path = f"images/{template_image}"
    while time.time() - start_time < timeout:
        if not running: return False
        try:
            screenshot = pyautogui.screenshot()
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                print(f"[ERROR] Template image not found at {template_path}")
                return False
            result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= confidence:
                template_width, template_height = template.shape[1], template.shape[0]
                center_x = max_loc[0] + template_width // 2
                center_y = max_loc[1] + template_height // 2
                
                autoit.mouse_move(x=center_x, y=center_y, speed=random.randint(5, 10))
                autoit.mouse_click(button="left", x=center_x, y=center_y)
                
                return True

        except Exception as e:
            print(f"[ERROR] An error occurred in find_and_click: {e}")
        time.sleep(0.5)
    print(f"[WARN] Could not find '{template_image}' on screen after {timeout} seconds.")
    return False

def long_sleep_with_stop_check(duration_seconds):
    end_time = time.time() + duration_seconds
    while time.time() < end_time:
        if not running:
            return
        time.sleep(0.1)

def main():
    print("Starting in 5 seconds. OPEN ROBLOX WINDOW.")
    print("Make sure you are NOT in shift lock.")
    time.sleep(5)

    while running:
        print("[ACTION] Engaging Shift Lock for mining...")
        autoit.send("{CTRLDOWN}")
        time.sleep(random.uniform(0.05, 0.1))
        autoit.send("{CTRLUP}")
        time.sleep(1)

        print("[ACTION] Mining...")
        autoit.mouse_down("left")
        long_sleep_with_stop_check(random.uniform(600, 720))
        autoit.mouse_up("left")
        if not running: break
        time.sleep(1)

        print("[ACTION] Disengaging Shift Lock to free mouse...")
        autoit.send("{CTRLDOWN}")
        time.sleep(random.uniform(0.05, 0.1))
        autoit.send("{CTRLUP}")
        time.sleep(1.5)

        print("[ACTION] Opening inventory...")
        autoit.send("t")
        time.sleep(1.5)

        if not find_and_click("sell_button.png"):
            print("[WARN] Sell button not found. Resetting by clicking Exit.")
            find_and_click("exit_button.png", timeout=2) 
            continue
        time.sleep(1.5)
        
        if not find_and_click("select_all_button.png"):
            print("[WARN] Select All button not found. Resetting by clicking Exit.")
            find_and_click("exit_button.png", timeout=2)
            continue
        time.sleep(1)

        if not find_and_click("accept_button.png"):
            print("[WARN] Accept button not found. Resetting by clicking Exit.")
            find_and_click("exit_button.png", timeout=2)
            continue
        time.sleep(1)

        if not find_and_click("confirm_yes_button.png"):
            print("[WARN] Confirm button not found. Resetting by clicking Exit.")
            find_and_click("exit_button.png", timeout=2)
            continue
        print("  -> Sale confirmed!")
        time.sleep(1.5)
        
        print("[ACTION] Clicking exit button to close menu...")
        if not find_and_click("exit_button.png"):
            print("[WARN] Could not find final exit button. The script may be stuck.")
        
        print("\n--- Cycle Complete ---\n")
        time.sleep(random.uniform(4, 5))

    print("\n[INFO] Script has been stopped by the user.")

if __name__ == "__main__":
    listener_thread = threading.Thread(target=stop_key_listener, daemon=True)
    listener_thread.start()
    main()