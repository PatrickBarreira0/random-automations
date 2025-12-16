import autoit
import time
import random
from keyboard_handler import is_running
from image_utils import find_and_click
from ocr_utils import extract_money_amount

def long_sleep_with_stop_check(duration_seconds):
    end_time = time.time() + duration_seconds
    while time.time() < end_time:
        if not is_running():
            return
        time.sleep(0.1)

def execute_mining_cycle(money_amounts):
    print("[ACTION] Engaging Shift Lock for mining...")
    autoit.send("{CTRLDOWN}")
    time.sleep(random.uniform(0.05, 0.1))
    autoit.send("{CTRLUP}")
    time.sleep(1)

    print("[ACTION] Mining...")
    autoit.mouse_down("left")
    long_sleep_with_stop_check(random.uniform(900, 1000))
    autoit.mouse_up("left")
    if not is_running(): 
        return False
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
        return True

    time.sleep(1.5)
    
    if not find_and_click("select_all_button.png"):
        print("[WARN] Select All button not found. Resetting by clicking Exit.")
        find_and_click("exit_button.png", timeout=2)
        return True

    time.sleep(1)

    if not find_and_click("accept_button.png"):
        print("[WARN] Accept button not found. Resetting by clicking Exit.")
        find_and_click("exit_button.png", timeout=2)
        return True

    time.sleep(1)

    money = extract_money_amount()
    if money is not None:
        money_amounts.append(money)

    if not find_and_click("confirm_yes_button.png"):
        print("[WARN] Confirm button not found. Resetting by clicking Exit.")
        find_and_click("exit_button.png", timeout=2)
        return True

    print("  -> Sale confirmed!")
    time.sleep(1.5)
    
    print("[ACTION] Clicking exit button to close menu...")
    if not find_and_click("exit_button.png"):
        print("[WARN] Could not find final exit button. The script may be stuck.")
    
    print("\n--- Cycle Complete ---\n")
    time.sleep(random.uniform(4, 5))
    return True

def run_automation():
    print("Starting in 5 seconds. OPEN ROBLOX WINDOW.")
    print("Make sure you are NOT in shift lock.")
    time.sleep(5)

    money_amounts = []

    while is_running():
        if not execute_mining_cycle(money_amounts):
            break

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
    
    return money_amounts

