import cv2, numpy as np, mss, glob, os, re
from pathlib import Path

# Load templates
templates = {
    Path(p).stem: cv2.imread(p, cv2.IMREAD_GRAYSCALE)
    for p in glob.glob("/Users/samlee/Desktop/project_balatro/templates/*.png")
}

# Define 8 MON regions
MONS = [
    {"top": 633, "left": 450, "width": 125, "height": 200},
    {"top": 633, "left": 587, "width": 125, "height": 200},
    {"top": 633, "left": 695, "width": 125, "height": 200},
    {"top": 633, "left": 806, "width": 125, "height": 200},
    {"top": 633, "left": 915, "width": 125, "height": 200},
    {"top": 633, "left": 1029, "width": 125, "height": 200},
    {"top": 633, "left": 1140, "width": 125, "height": 200},
    {"top": 633, "left": 1253, "width": 125, "height": 200}
]

THR = 0.8
sct = mss.mss()

def detect_hand_cards():
    current_detected = []
    for idx, MON in enumerate(MONS):
        frame = np.array(sct.grab(MON))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)

        best_match = None
        for name, tmpl in templates.items():
            res = cv2.matchTemplate(gray, tmpl, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val > THR:
                h, w = tmpl.shape
                if not best_match or max_val > best_match[1]:
                    best_match = (name, max_val, max_loc, (w, h))

        if best_match:
            name, val, (x, y), (w, h) = best_match
            base_name = re.match(r'^([A2-9JQK10]{1,2}[CDHS])', name)
            card_label = base_name.group(1) if base_name else name
            current_detected.append(f"{card_label}:{val:.2f}")
    
    return current_detected