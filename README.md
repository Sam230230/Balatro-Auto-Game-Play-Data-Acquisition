# Project Balatro – Automated Gameplay Data Generation with Decision making Optimization

Author: Sangmyeong Lee \
Contact: hismyeong@gmail.com \
Supervisor: Haixu Wang 
---

## Project description

This project automates gameplay of Balatro to generate datasets for model training and testing in the development of a poker game tutorial AI. 
It leverages **Maximum Likelihood Estimation (MLE)** and **gradient descent** within a **Markov chain framework** to optimize decision-making between **hand plays** and **discards**.

---

## Requirements
 - Any types of 15-inches screen laptop or monitor.
 - dual screen setup (recommended).
 - Important libraries: pyautogui, easyocr, pytesseract, cv2, numpy.

---
## Project Structure

project_balatro/
- BLTR_controller.py .......... Core gameplay automation  
- play_balatro_par_optim.py ... Optimization loop (MLE, transition matrix updates)  
- cards_detect_fn.py .......... Card detection (OCR / template matching)  
- auto_card_selector.py ....... Auto-select 5 cards out of 8
- game_end_info_detect.py ..... OCR functions to extract game stats  
- gameplay_log.json ........... Log of all gameplay sessions  
- README.md   

---

## How to Run

1. Set up a dual-screen environment: one screen running **Balatro** and the other for executing **BLTR_controller.py**.
2. Adjust the Balatro game window to **1709 × 976** resolution.
3. Navigate to the **blind selection stage** in Balatro.
4. Run `BLTR_controller.py` from your terminal or IDE to start automated gameplay.