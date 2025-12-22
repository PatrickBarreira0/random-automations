import pyautogui
import cv2
import numpy as np
import pytesseract
import re
import time
from config import CONFIDENCE_LEVEL

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
        
        roi_width = 400
        x1 = max(0, yes_button_x - roi_width // 2 + 100)
        y1 = max(0, yes_button_y - 70)
        x2 = min(screenshot_cv.shape[1], yes_button_x + roi_width // 2 + 100)
        y2 = min(screenshot_cv.shape[0], yes_button_y + 60)
        
        if y2 <= y1 or x2 <= x1:
            return None
        
        roi_gray = gray[y1:y2, x1:x2]
        _, thresh = cv2.threshold(roi_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        kernel = np.ones((2, 2), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        roi_resized = cv2.resize(thresh, (thresh.shape[1] * 3, thresh.shape[0] * 3), interpolation=cv2.INTER_CUBIC)
        
        try:
            custom_config = r'--oem 3 --psm 11 -c tessedit_char_whitelist=0123456789.,'
            text = pytesseract.image_to_string(roi_resized, config=custom_config)
            
            if not text.strip() or len(text.strip()) < 3:
                custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.,'
                text = pytesseract.image_to_string(roi_resized, config=custom_config)
            
            if not text.strip() or len(text.strip()) < 3:
                custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789.,'
                text = pytesseract.image_to_string(roi_resized, config=custom_config)
            
            if not text.strip() or len(text.strip()) < 3:
                text = pytesseract.image_to_string(roi_resized, config='--oem 3 --psm 6')
        except:
            return None
        
        text_cleaned = text.replace(' ', '').replace('\n', '').replace('?', '').replace('!', '')
        text_cleaned = re.sub(r'[^\d.,]', '', text_cleaned)
        
        patterns = [
            r'\d{1,3}(?:\.\d{3})*,\d{1,2}',
            r'\d{1,3}(?:,\d{3})*\.\d{1,2}',
            r'\d{1,3}(?:\.\d{3})+',
            r'\d{1,3}(?:,\d{3})+',
            r'\d+\.\d+',
            r'\d+,\d+',
            r'\d+'
        ]
        
        all_matches = []
        for pattern in patterns:
            matches = re.findall(pattern, text_cleaned)
            all_matches.extend(matches)
        
        all_matches = list(set(all_matches))
        
        if all_matches:
            valid_amounts = []
            for match in all_matches:
                try:
                    match_clean = match
                    
                    if ',' in match_clean and '.' in match_clean:
                        comma_pos = match_clean.rindex(',')
                        period_pos = match_clean.rindex('.')
                        if comma_pos > period_pos:
                            amount_str = match_clean.replace('.', '').replace(',', '.')
                        else:
                            amount_str = match_clean.replace(',', '')
                    elif ',' in match_clean:
                        parts = match_clean.split(',')
                        if len(parts) == 2 and len(parts[1]) <= 2:
                            if '.' in parts[0]:
                                amount_str = parts[0].replace('.', '') + '.' + parts[1]
                            else:
                                amount_str = match_clean.replace(',', '.')
                        else:
                            amount_str = match_clean.replace(',', '')
                    elif '.' in match_clean:
                        parts = match_clean.split('.')
                        if len(parts) == 2:
                            amount_str = match_clean
                        elif len(parts[-1]) <= 2:
                            amount_str = ''.join(parts[:-1]) + '.' + parts[-1]
                        else:
                            amount_str = match_clean.replace('.', '')
                    else:
                        amount_str = match_clean
                    
                    amount = float(amount_str)
                    if amount > 10:
                        valid_amounts.append(amount)
                except ValueError:
                    continue
            
            if valid_amounts:
                return max(valid_amounts)
        
        return None
    except:
        return None


