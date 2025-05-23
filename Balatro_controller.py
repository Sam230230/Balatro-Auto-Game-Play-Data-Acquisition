import pyautogui as pag
import time
import tkinter as tk
import threading


CARD_POSITIONS = {
    1: (500, 700),
    2: (600, 700),
    3: (730, 700),
    4: (830, 700),
    5: (960, 700),
    6: (1080, 700),
    7: (1200, 700),
    8: (1300, 700)
}

BUTTONS = {
    "hand": (739, 950),
    "discard": (1135, 950)
}

BLINDS = {
    "select small": (616, 391),
    "select big": (937, 391),
    "select boss": (1251, 391)
}

SKIP_BLINDS = {
    "skip small": (644, 820),
    "skip big": (939, 820)
}

CASH_OUT_JOKER = {
    "cash out": (934, 450),
    "next round": (607, 494)
}

print("Switch to Balatro — clicking starts in 3 seconds...")
pag.click(x=2793, y=771)

# Set up the game stage
def click_blind():
    time.sleep(3)

    print("Select blind: [select small, select big, select boss, skip small, skip big]")
    blind = input().strip().lower()

    pag.click(x=929, y=528) # Click to focus the game window
    pag.click(x=2793, y=771) # Click to focus the terminal window
    if blind in BLINDS:
        x, y = BLINDS[blind]
        pag.click(x=929, y=528)
        pag.moveTo(x, y, 1)
        time.sleep(1)
        pag.click(x, y)
        pag.click(x=2793, y=771)
        print(f"[Click] at {x},{y}")
        return play_turn()
    
    pag.click(x=929, y=528) # Click to focus the game window
    if blind in SKIP_BLINDS:
        x, y = SKIP_BLINDS[blind]
        pag.moveTo(x, y, 1)
        time.sleep(1)
        pag.click(x, y)
        pag.click(x=2793, y=771)
        print(f"[Click] at {x},{y}")
        return click_blind()
    
    return "invalid"

def play_turn():
    while True:
        time.sleep(2)

        print("Select cards by index (e.g., 1 3 5) or type 'cash out':")
        selected_raw = input().strip().lower()

        if selected_raw == "cash out":
              
            pag.click(19, 95, 1)  
            pag.click(947, 358, 1)  # Click to focus the game window(cash out)
            x, y = CASH_OUT_JOKER["cash out"]
            pag.click(x, y)
            print(f"[Click] at {x},{y}")
            return Joker()

        selected = list(map(int, selected_raw.split()))

        print("Choose action: [hand, discard]")
        action = input().strip().lower()

        # Click game window
        pag.click(x=929, y=528)

        # Click selected cards
        for i in selected:
            x, y = CARD_POSITIONS[i]
            pag.moveTo(x, y, 1)
            time.sleep(0.3)
            pag.click(x, y)
            print(f"[Click] at {x},{y}")
            time.sleep(0.3)

        # Click hand or discard
        if action in BUTTONS:
            x, y = BUTTONS[action]
            pag.moveTo(x, y, 1)
            time.sleep(0.3)
            pag.click(x, y)
            pag.click(x=2793, y=771)
            print(f"[Click] at {x},{y}")
            time.sleep(0.3)

def Joker():
    print("Buy whatever you want, then type 'next round'.")
    next_round = input().strip().lower()
    if next_round == "next round":
        x, y = CASH_OUT_JOKER["next round"]
        pag.click(x=19, y=95)
        pag.click(x, y, 1)
    pag.click(x=2793, y=771)  
    return click_blind()  # Click to focus the game window


result = click_blind()
if result == "invalid":
    print("Invalid choice. Please restart or handle error.")

# Game start
print("Game started. Waiting for blind selection...")
click_blind()