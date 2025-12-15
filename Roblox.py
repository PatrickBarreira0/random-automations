import pyautogui
import autoit
import cv2
import numpy as np
import time
import random
import threading
import keyboard
import pytesseract
import re
import os

CONFIDENCE_LEVEL = 0.8
STOP_KEY = 'k'
running = True
money_amounts = []

tesseract_paths = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME', '')),
]

for path in tesseract_paths:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        break
else:
    try:
        pytesseract.get_tesseract_version()
    except:
        pass

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

def extract_money_amount():
    try:
        time.sleep(0.5)
        screenshot = pyautogui.screenshot()
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        yes_button_found = False
        yes_button_x, yes_button_y = 0, 0
        
        try:
            yes_template = cv2.imread("images/confirm_yes_button.png", cv2.IMREAD_COLOR)
            if yes_template is not None:
                result = cv2.matchTemplate(screenshot_cv, yes_template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                if max_val >= CONFIDENCE_LEVEL:
                    template_width = yes_template.shape[1]
                    yes_button_x = max_loc[0] + template_width // 2
                    yes_button_y = max_loc[1]
                    yes_button_found = True
        except:
            pass
        
        if not yes_button_found:
            return None
        
        gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        roi_width = 400
        x1 = max(0, yes_button_x - roi_width // 2 + 100)
        y1 = max(0, yes_button_y - 70)
        x2 = min(screenshot_cv.shape[1], yes_button_x + roi_width // 2 + 100)
        y2 = min(screenshot_cv.shape[0], yes_button_y + 60)
        
        if y2 <= y1 or x2 <= x1:
            return None
        
        roi = thresh[y1:y2, x1:x2]
        roi_resized = cv2.resize(roi, (roi.shape[1] * 2, roi.shape[0] * 2), interpolation=cv2.INTER_CUBIC)
        
        try:
            custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789.,'
            text = pytesseract.image_to_string(roi_resized, config=custom_config)
            
            if not text.strip():
                custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.,'
                text = pytesseract.image_to_string(roi_resized, config=custom_config)
            
            if not text.strip():
                text = pytesseract.image_to_string(roi_resized, config='--oem 3 --psm 6')
        except:
            return None
        
        pattern = r'\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+\.\d+'
        matches = re.findall(pattern, text)
        
        if matches:
            for match in matches:
                try:
                    amount_str = match.replace(',', '')
                    amount = float(amount_str)
                    if amount > 0:
                        return amount
                except ValueError:
                    continue
        
        return None
    except:
        return None

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
        long_sleep_with_stop_check(random.uniform(900, 1000))
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

        money = extract_money_amount()
        if money is not None:
            money_amounts.append(money)

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
    
    if money_amounts:
        total = sum(money_amounts)
        print(f"\n{'='*50}")
        print(f"TOTAL CYCLES: {len(money_amounts)}")
        print(f"TOTAL MONEY EARNED: {total:,.2f}")
        print(f"AVERAGE PER CYCLE: {total/len(money_amounts):,.2f}")
        print(f"{'='*50}")
    else:
        print("\n[INFO] No money amounts were recorded.")

if __name__ == "__main__":
    listener_thread = threading.Thread(target=stop_key_listener, daemon=True)
    listener_thread.start()
    main()