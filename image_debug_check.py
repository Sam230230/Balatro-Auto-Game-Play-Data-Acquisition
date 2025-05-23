import cv2, numpy as np, mss, time, glob, os
from pathlib import Path
import re

# templates 
templates = {
    Path(p).stem: cv2.imread(p, cv2.IMREAD_GRAYSCALE)
    for p in glob.glob("/Users/samlee/Desktop/project_balatro/templates/*.png")
}
print(f"Loaded {len(templates)} templates.")

# capture region
MON = {"top": 633, "left": 450, "width": 980, "height": 200}
sct = mss.mss()

THR = 0.3           # threshold
cv2.namedWindow("debug", cv2.WINDOW_NORMAL)

while True:
    frame = np.array(sct.grab(MON))
    gray  = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)

    hits = []
    for name, tmpl in templates.items():
        res = cv2.matchTemplate(gray, tmpl, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        if max_val > THR:
            h, w = tmpl.shape
            hits.append((name, max_val, max_loc, (w, h)))

    # draw rectangles
    vis = frame.copy()
    for name, val, (x, y), (w, h) in hits:
        cv2.rectangle(vis, (x, y), (x+w, y+h), (0,0,255), 2)
        cv2.putText(vis, name, (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)

    # show and print
    cv2.imshow("debug", vis[..., :3])
    if hits:
        best = sorted(hits, key=lambda t: -t[1])[:5]
        print("Detected:", [f"{n}:{v:.2f}" for n, v, *_ in best])

    if cv2.waitKey(30) & 0xFF == 27:   # Esc quits
        break

cv2.destroyAllWindows()
