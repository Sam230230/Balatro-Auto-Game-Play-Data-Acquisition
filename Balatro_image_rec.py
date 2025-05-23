import cv2, numpy as np, mss, time, glob
from pathlib import Path
from collections import defaultdict

CARD_W, CARD_H = 80, 110   # full card face size in pixels
THR = 0.80                 # similarity threshold
last_hand = []

# load templates 
'''templates = {}
for p in glob.glob("/Users/samlee/Desktop/project_balatro/templates/*.png"):
    img = cv2.imread(p, cv2.IMREAD_COLOR)  # load colour
    img = cv2.resize(img, (CARD_W, CARD_H), interpolation=cv2.INTER_AREA)
    templates[Path(p).stem] = img'''

templates = defaultdict(list)
for p in glob.glob("/Users/samlee/Desktop/project_balatro/templates/*.png"):
    img = cv2.imread(p, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (CARD_W, CARD_H), interpolation=cv2.INTER_AREA)
    name = Path(p).stem.split('_')[0]  # 'QS_1' -> 'QS'
    templates[name].append(img)


# screen capture config 
MON = {"top": 633, "left": 450, "width": 1000, "height": 200}  # adjust to the hand region
sct = mss.mss()

def detect_cards(img_bgr):
    img_gray = cv2.GaussianBlur(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY), (3, 3), 0)
    matches = []
    for name, variant_list in templates.items():
        for tmpl in variant_list:
            tmpl_gray = cv2.GaussianBlur(cv2.cvtColor(tmpl, cv2.COLOR_BGR2GRAY), (3, 3), 0)
            res = cv2.matchTemplate(img_gray, tmpl_gray, cv2.TM_CCOEFF_NORMED)
            max_val = res.max()
            print(f"{name}: max score = {res.max():.4f}")
            if max_val >= THR:
                _, _, _, max_loc = cv2.minMaxLoc(res)
                matches.append((max_loc[0], name, max_val))

    # Sort by horizontal (x) position
    matches.sort(key=lambda x: x[0])

    seen = set()
    hand = []
    for x, name, score in matches:
        if name not in seen:
            hand.append(name)
            seen.add(name)
        if len(hand) == 8:
            break

    return hand

print("Detecting hand…  (Ctrl-C to quit)")
try:
    while True:
        frame = np.array(sct.grab(MON))[..., :3]   # BGRA -> BGR
        hand  = detect_cards(frame)

        if len(hand) == 8 and hand != last_hand:
            print("Current hand:", hand)
            last_hand = hand

        time.sleep(0.5)
except KeyboardInterrupt:
    print("bye")

#-------------------------------------------------------------------

