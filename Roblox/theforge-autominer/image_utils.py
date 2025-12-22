import pyautogui
import autoit
import cv2
import numpy as np
import time
import random
from config import CONFIDENCE_LEVEL
from keyboard_handler import is_running

def find_and_click(template_image, confidence=CONFIDENCE_LEVEL, timeout=5):
    start_time = time.time()
    template_path = f"images/{template_image}"
    while time.time() - start_time < timeout:
        if not is_running(): 
            return False
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


