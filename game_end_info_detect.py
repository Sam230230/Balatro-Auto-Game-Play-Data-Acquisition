import cv2, numpy as np, mss, pytesseract
from pathlib import Path
import easyocr

GAME_END_INFO = {
    "Goal score": {"top": 275, "left": 266, "width": 166, "height": 44},    #after winning the game goal score position: {"top": 563, "left": 660, "width": 325, "height": 50}
    "goal score in play": {"top": 275, "left": 266, "width": 166, "height": 44},
    "Round score": {"top": 425, "left": 190, "width": 325, "height": 47},
    "Hands left": {"top": 715, "left": 225, "width": 100, "height": 56},
    "Discards left": {"top": 715, "left": 340, "width": 100, "height": 56},
    "Cash earned": {"top": 424, "left": 1015, "width": 144, "height": 70},
    "Ante": {"top": 915, "left": 225, "width": 43, "height": 60},
    "Round": {"top": 915, "left": 342, "width": 100, "height": 60}
}

GAME_OVER_INFO = {
    "Goal score": {"top": 275, "left": 266, "width": 166, "height": 44},
    "Round score": {"top": 425, "left": 190, "width": 280, "height": 47},
    "Hands left": {"top": 715, "left": 225, "width": 100, "height": 56},
    "Discards left": {"top": 715, "left": 340, "width": 100, "height": 56},
    "Ante": {"top": 915, "left": 225, "width": 43, "height": 60},
    "Round": {"top": 915, "left": 342, "width": 100, "height": 60}
}

POKER_HANDS = {
    "Straight Flush": {"top": 100, "left": 100, "width": 200, "height": 50},
    "Four of a Kind": {"top": 200, "left": 100, "width": 200, "height": 50},
    "Full House": {"top": 300, "left": 100, "width": 200, "height": 50},
    "Flush": {"top": 400, "left": 100, "width": 200, "height": 50},
    "Straight": {"top": 500, "left": 100, "width": 200, "height": 50},  
    "Three of a Kind": {"top": 600, "left": 100, "width": 200, "height": 50},
    "Two Pair": {"top": 700, "left": 100, "width": 200, "height": 50},
    "Pair": {"top": 800, "left": 100, "width": 200, "height": 50},
    "High Card": {"top": 900, "left": 100, "width": 200, "height": 50}
}

sct = mss.mss()

reader = easyocr.Reader(['en'])

def extract_game_end_info(debug=False):
    info = {}

    for label, region in GAME_END_INFO.items():
        frame = np.array(sct.grab(region))
        
        # Focus on weighted red-channel grayscale
        b, g, r, _ = cv2.split(frame)
        gray = 0.2 * b + 0.2 * g + 0.6 * r
        gray = gray.astype(np.uint8)
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # Apply threshold
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        thresh = cv2.bitwise_not(thresh)

        # Run EasyOCR on the thresholded image
        result = reader.readtext(thresh, detail=0)
        text = result[0] if result else ""

        text_clean = ''.join(filter(str.isdigit, text))
        info[label] = int(text_clean) if text_clean.isdigit() else None

        if debug:
            print(f"{label}: {text_clean}")
            cv2.imshow(f"debug_{label}", thresh)
            cv2.imshow(f"debug_raw_{label}", frame)

    if debug:
        print("Extracted Info:", info)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    if info.get("Goal score") is not None and info.get("Round score") is not None:
        info["Additional score achieved"] = abs(info["Goal score"] - info["Round score"])

    return info

def extract_game_over_info(debug=False):
    info = {}

    for label, region in GAME_OVER_INFO.items():
        frame = np.array(sct.grab(region))
        
        # Focus on weighted red-channel grayscale
        b, g, r, _ = cv2.split(frame)
        gray = 0.2 * b + 0.2 * g + 0.6 * r
        gray = gray.astype(np.uint8)
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # Apply threshold
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        thresh = cv2.bitwise_not(thresh)

        # Run EasyOCR on the thresholded image
        result = reader.readtext(thresh, detail=0)
        text = result[0] if result else ""

        text_clean = ''.join(filter(str.isdigit, text))
        info[label] = int(text_clean) if text_clean.isdigit() else None

        if debug:
            print(f"{label}: {text_clean}")
            cv2.imshow(f"debug_{label}", thresh)
            cv2.imshow(f"debug_raw_{label}", frame)

    if debug:
        print("Extracted Info:", info)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return info



#extract_game_end_info(debug=True)
#extract_game_over_info(debug=True)

       
