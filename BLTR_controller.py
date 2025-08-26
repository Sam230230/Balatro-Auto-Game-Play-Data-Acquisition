import pyautogui as pag
import time
import json
import random
from datetime import datetime
import os

from play_balatro_par_optim import optimize_params

# per-game in-memory buffers (actions and rewards)
X_SEQ_BUFFER = []  # actions: 0=hand, 1=discard
Y_SEQ_BUFFER = []  # rewards: score_earned for each action

# path to store learned parameters for next game
base_dir = os.path.dirname(__file__)
out_path = os.path.join(base_dir, "transition_params.json")

from cards_detect_fn import detect_hand_cards
from auto_card_selector import auto_select_cards
from game_end_info_detect import extract_game_end_info, extract_game_over_info

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
    "0": (739, 950), # Hand
    "1": (1135, 950) # Discard
}

BLINDS = {
    "small": (616, 391),
    "big": (937, 391),
    "boss": (1251, 391)
}

SKIP_BLINDS = {
    "skip small": (644, 820),
    "skip big": (939, 820)
}

CASH_OUT = {
    "cash out": (934, 450),
    "next round": (607, 494)
}

print("Switch to Balatro")

'''
pag.click(x=3793, y=1334) # Click terminal area Monitor
#pag.click(x=2793, y=234) # Click termianl area Ipad
'''

# Set up the game stage
def click_blind(selected_raw=None):
    '''
        1. Manual blind selection
    print("Select blind: [small, big, boss, skip small, skip big]")
    blind = input().strip().lower()
    '''
    time.sleep(1)

    # Decide the blind to play based on game state
    if selected_raw == "game over" or selected_raw is None:
        blind = "small"
    elif selected_raw == "cash out":
        blind = getattr(click_blind, "last_blind", "small")
        if blind == "small":
            blind = "big"
        elif blind == "big":
            blind = "boss"
        else:
            blind = "small"  # After boss, restart or handle differently

    click_blind.last_blind = blind

    print(f"Select blind: {blind}")

    '''pag.click(x=929, y=528) # Click to focus the game window
    pag.click(x=2793, y=771) # Click to focus the terminal window'''

    if blind in BLINDS:
        x, y = BLINDS[blind]
        pag.click(x=929, y=528)
        pag.moveTo(x, y)
        time.sleep(1)
        pag.click(x, y)
        pag.click(x=2793, y=771)
        print(f"[Click] at {x},{y}")
        return play_turn(blind)
    
    pag.click(x=929, y=528) # Click to focus the game window
    if blind in SKIP_BLINDS:
        x, y = SKIP_BLINDS[blind]
        pag.moveTo(x, y)
        time.sleep(1)
        pag.click(x, y)
        pag.click(x=2793, y=771)
        print(f"[Click] at {x},{y}")

        '''
        # Log skip blind as final action
        entry = {
            "timestamp": datetime.now().isoformat(),
            "blind": blind,
            "actions": [{
                "hand": [],
                "cards_played": [],
                "action": blind,
                "result": blind
            }]
        }

        log_path = os.path.join(os.path.dirname(__file__), "gameplay_log.json")
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

        return click_blind()'''

    return "invalid"

def play_turn(blind):
    actions = []
    history = []
    hand_count = 0
    discard_count = 0
    # reset per-game buffers
    X_SEQ_BUFFER.clear()
    Y_SEQ_BUFFER.clear()
    # Baseline of the last seen cumulative Round score (start from 0 at the beginning of a round)
    last_round_score = 0

    while True:
        selected_raw = None
        
        game_end_info = extract_game_end_info(debug=False)
        game_over_info = extract_game_over_info(debug=False)
        hands_left = game_end_info.get("Hands left")
        goal = game_end_info.get("goal score in play")
        score = game_end_info.get("Round score")
        
        #------------------------------------------ Check game end conditions 1 -----------------------------------
        time.sleep(3)
        cards = detect_hand_cards()
        print(f"[DEBUG_1] hands_left: {hands_left}, goal: {goal}, score: {score}")
        print("Detected cards 1:", cards)

        # Use last seen cumulative Round score as the pre-action baseline for this turn
        current_score = last_round_score

        if hands_left is None and len(cards) <= 1 and (score is None or score < goal):
            selected_raw = "game over"
            actions.append({
                "hand": cards,
                "cards_played": [],
                "action": "game_over",
                "result": "game_over",
                "game_over_info": game_over_info
            })
            break
        
        
        # *** Important ***
        # If the game is 'in_progress' len(cards) should be 8, so this block should not be executed.
        # If len(cards) < 8, it means the game is not in progress, likely 'game over' or 'cash out'.
        # However, it this block is executed, it might be a card detection issue.

        #if len(cards) < 8 and selected_raw not in ["game_over", "cash_out"]:
            print("[WARN] Incomplete hand detected. Skipping this turn.")
            time.sleep(2)
            continue
        
        
        if goal is not None and score is not None and score >= goal:
            selected_raw = "cash out"
            actions.append({
                "hand": cards,
                "cards_played": [],
                "action": "cash_out",
                "result": "cash_out",
                "game_end_info": game_end_info
            })
            break

        if selected_raw is None:
            pass  

        '''   
            # 1. Manual card selection

        input("Press Enter to detect cards in hand...")
        time.sleep(3)
        cards = detect_hand_cards()
        print("Detected cards 1:", cards)

        #print("Select cards by index (e.g., 1 3 5) or type 'cash out' or 'game over':")
        #selected_raw = input().strip().lower()
        '''

        #------------------------------- Auto-select cards --------------------------------
        #if selected_raw == "":
        selected = auto_select_cards(cards, history)
        print("Auto-selected card indices:", selected)
        selected_raw = ' '.join(str(i) for i in selected)
        #-----------------------------------------------------------------------------------

        '''
            # 2.  Manual game end actions

        if selected_raw == "cash out": 

            game_end_info = extract_game_end_info(debug=False)

            time.sleep(0.2)
            pag.click(19, 95)
            time.sleep(0.2)
            pag.click(947, 358)
            x, y = CASH_OUT["cash out"]
            pag.click(19, 95)
            pag.click(x, y)
            print(f"[Click] at {x},{y}")

            # Log cash out as final action
            actions.append({
                "hand": cards,
                "cards_played": [],
                "action": "cash_out",
                "result": "cash_out",
                "game_end_info": game_end_info
            })

            break  # Exit the loop to log and go to next_stage()
        
        if selected_raw == "game over":
            print("Game over. Exiting...")

            # Log game over as final action
            actions.append({
                "hand": cards,
                "cards_played": [],
                "action": "game_over",
                "result": "game_over"
            })

            break  # Exit the loop to log and go to next_stage()

        selected = list(map(int, selected_raw.split()))
        '''

        '''
        # 3. Manual action selection
        print("Choose action: [hand = 0, discard = 1]")
        action = input().strip().lower()
        '''

        #-------------------------------- Hand and discard counts and selection --------------------------------
        '''
        remaining_hand = 4 - hand_count
        remaining_discard = 4 - discard_count

        valid_actions = ["0"] * remaining_hand + ["1"] * remaining_discard

        if not valid_actions:
            break

        action = random.choice(valid_actions)
        print(f"Auto-selected action: {action}")

        if action == "0":
            hand_count += 1
        elif action == "1":
            discard_count += 1
        '''

        TRANSITION_MATRIX = {
            "0": {"0": 0.5, "1": 0.5},
            "1": {"0": 0.6, "1": 0.4}
        }

        # Track previous action
        last_action = None  # Initialize at the top of play_turn()

        # Inside the game loop:
        remaining_hand = 4 - hand_count
        remaining_discard = 4 - discard_count

        # Filter valid options
        valid_actions = []
        if remaining_hand > 0:
            valid_actions.append("0")  # hand
        if remaining_discard > 0:
            valid_actions.append("1")  # discard

        if not valid_actions:
            break  # No moves left

        # Use transition matrix
        if last_action is None:
            # Initial step: equal chance
            action = random.choice(valid_actions)
        else:
            probs = TRANSITION_MATRIX[last_action]
            weights = [probs[a] for a in valid_actions]
            total = sum(weights)
            normalized = [w / total for w in weights]
            action = random.choices(valid_actions, weights=normalized)[0]

        # Count usage
        if action == "0":
            hand_count += 1
        elif action == "1":
            discard_count += 1

        last_action = action  # Update last_action
        print(f"Auto-selected action: {action}")
        #-----------------------------------------------------------------------------------------

        #---------------------------------- Cards clicking action -------------------------------
        pag.click(x=929, y=528)

        try:
            for i in selected:
                x, y = CARD_POSITIONS[i]
                pag.moveTo(x, y)
                time.sleep(0.3)
                pag.click(x, y)
                print(f"[Click] at {x},{y}, {cards[i - 1]}")
                time.sleep(0.3)
        except IndexError:
            continue 


        if action in BUTTONS:
            x, y = BUTTONS[action]
            pag.moveTo(x, y)
            time.sleep(0.3)
            pag.click(x, y)
            pag.click(x=2793, y=771)
            print(f"[Click] at {x},{y}")
            time.sleep(0.3)
        #-----------------------------------------------------------------------------------------

        # Store each action
        actions.append({
            "hand": cards,
            "cards_played": [cards[i - 1] for i in selected],
            "action": action,
            "result": "in_progress"
        })

        # Store history of played cards
        history.append(sorted([cards[i - 1] for i in selected]))


        #------------------------------------------ Check game end conditions 2 -----------------------------------
        # Re-read game info after the click to get the updated score
        time.sleep(4)
        post_info = extract_game_end_info(debug=False)
        hands_left = post_info.get("Hands left")
        goal = post_info.get("goal score in play")
        score_after = post_info.get("Round score")

        # If Hands left is None, we may already be on the game-over / cash-out screen.
        # In that case, prefer the Game-Over OCR regions for an authoritative Round score.
        if hands_left is None:
            go_info_for_delta = extract_game_over_info(debug=False)
            go_round_score = go_info_for_delta.get("Round score")
            if go_round_score is not None:
                score_after = go_round_score

        # Attach per-turn metrics using new naming:
        # current_score: cumulative score before this action
        # score_earned: absolute increment this action produced
        actions[-1]["current_score"] = current_score
        if score_after is not None:
            actions[-1]["score_earned"] = abs(score_after - current_score)
        else:
            actions[-1]["score_earned"] = None

        # buffer sequences for optimizer (use 0 reward if OCR failed)
        X_SEQ_BUFFER.append(int(action))
        Y_SEQ_BUFFER.append(0 if actions[-1]["score_earned"] is None else actions[-1]["score_earned"])

        # Update baseline for the next action
        if score_after is not None:
            last_round_score = score_after

        cards = detect_hand_cards()
        print("Detected cards 2:", cards)
        print(f"[DEBUG_2] hands_left: {hands_left}, goal: {goal}, score: {score_after}, earned: {actions[-1]['score_earned']}")

        if hands_left is None and len(cards) <= 1 and score_after is not None and goal is not None and score_after < goal:
            selected_raw = "game over"
            # Re-extract from the Game Over overlay to avoid stale in-play values
            go_latest = extract_game_over_info(debug=False)
            # If OCR missed the round score here, but we already have score_after from GO region above, prefer it
            if go_latest.get("Round score") is None and score_after is not None:
                go_latest["Round score"] = score_after
            actions.append({
                "hand": cards,
                "cards_played": [],
                "action": "game_over",
                "result": "game_over",
                "game_over_info": go_latest
            })
            break

        if goal is not None and score_after is not None and score_after >= goal:
            selected_raw = "cash out"
            # Re-extract from the in-play/cash-out regions to ensure we log the latest score
            gei_latest = extract_game_end_info(debug=False)
            if gei_latest.get("Round score") is None and score_after is not None:
                gei_latest["Round score"] = score_after
            actions.append({
                "hand": cards,
                "cards_played": [],
                "action": "cash_out",
                "result": "cash_out",
                "game_end_info": gei_latest
            })
            break

        if selected_raw is None:
            pass
        #------------------------------------------------------------------------------------------------------


    #------------------------------------------ Log the final action -----------------------------------
    entry = {
        "timestamp": datetime.now().isoformat(),
        "blind": blind,
        "actions": actions
    }

    print("Writing gameplay log data:", entry)

    log_path = os.path.join(os.path.dirname(__file__), "gameplay_log.json")
    with open(log_path, "a") as f:
        #f.write(json.dumps(entry) + "\n")
        json.dump(entry, f, indent=2, sort_keys=False)
        f.write("\n")

    # ------------------ train params from this game & persist ------------------
    try:
        with open(out_path, "r") as f:
            init = json.load(f)
            init_params = {
                "q0": init.get("q0", 0.5),
                "p00": init.get("p00", 0.5),
                "p11": init.get("p11", 0.5),
                "z0": init.get("z0", 0.5),
                "z1": init.get("z1", 0.5),
            }
    except Exception:
        init_params = {"q0":0.5, "p00":0.5, "p11":0.5, "z0":0.5, "z1":0.5}

    try:
        result = optimize_params(X_SEQ_BUFFER, Y_SEQ_BUFFER, init_params=init_params, lr=0.3, steps=150, learn_q0=True)
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2)
        print("[AUTOTRAIN] Saved:", result)
    except Exception as e:
        print("[AUTOTRAIN] Skipped training due to error:", e)
    # --------------------------------------------------------------------------
        
    #------------------------------------------------------------------------------------------------------
    
    if selected_raw == "game over":
        print("Game over. New Run")
        time.sleep(1)
        pag.click(x=1092, y=818, clicks=2, interval=1.0) # Click 'new run' button
        time.sleep(1)
        pag.click(x=846, y=822, clicks=2, interval=1.0) # Click 'play' after new run
        time.sleep(3)
        return click_blind("game over")
        
    
    if selected_raw == "cash out":
        #print("Buy whatever you want, then type 'next round'.")
        #next_round = input().strip().lower()
        pag.click(19, 95)
        x, y = CASH_OUT["cash out"]
        pag.click(x, y)
        time.sleep(2)
        x, y = CASH_OUT["next round"]
        pag.click(x, y)
        time.sleep(2)  
        return click_blind("cash out")
        


result = click_blind()
if result == "invalid":
    print("Invalid choice. Please restart or handle error.")

