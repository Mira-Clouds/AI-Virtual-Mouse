import cv2
import mediapipe as mp
import pyautogui
import numpy as np

# 1. Setup MediaPipe & PyAutoGUI
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

screen_width, screen_height = pyautogui.size()
pyautogui.FAILSAFE = False

# Configuration Settings
smooth_factor = 4
margin_x, margin_y = 150, 150
prev_x, prev_y = 0, 0

cap = cv2.VideoCapture(0)

print("AI Virtual Mouse - Development Branch")
print("Gestures: Index=Move | Index+Thumb=LeftClick | Index+Middle=RightClick | Middle+Thumb=Scroll")

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Landmarks points (Index, Thumb, Middle)
            thumb_tip = hand_landmarks.landmark[4]
            index_tip = hand_landmarks.landmark[8]
            middle_tip = hand_landmarks.landmark[12]

            # Pixel coordinates
            ix, iy = int(index_tip.x * w), int(index_tip.y * h)
            tx, ty = int(thumb_tip.x * w), int(thumb_tip.y * h)
            mx, my = int(middle_tip.x * w), int(middle_tip.y * h)

            # --- 1. MOUSE MOVEMENT (Using Index Finger) ---
            mapped_x = np.interp(ix, (margin_x, w - margin_x), (0, screen_width))
            mapped_y = np.interp(iy, (margin_y, h - margin_y), (0, screen_height))
            
            curr_x = prev_x + (mapped_x - prev_x) / smooth_factor
            curr_y = prev_y + (mapped_y - prev_y) / smooth_factor
            
            try:
                pyautogui.moveTo(curr_x, curr_y)
            except: pass
            prev_x, prev_y = curr_x, curr_y

            # --- 2. LEFT CLICK (Index + Thumb) ---
            dist_left = np.hypot(ix - tx, iy - ty)
            if dist_left < 35:
                pyautogui.click()
                cv2.putText(frame, "LEFT CLICK", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                pyautogui.sleep(0.1)

            # --- 3. RIGHT CLICK (Index + Middle) ---
            dist_right = np.hypot(ix - mx, iy - my)
            if dist_right < 35:
                pyautogui.rightClick()
                cv2.putText(frame, "RIGHT CLICK", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                pyautogui.sleep(0.2)

            # --- 4. SCROLLING (Middle + Thumb) ---
            dist_scroll = np.hypot(mx - tx, my - ty)
            if dist_scroll < 35:
                # මැදැඟිල්ල උඩට පහළට කරන විට scroll වේ
                if my < (h / 2) - 30: # මැදට වඩා උඩින් ඇඟිල්ල තිබේ නම්
                    pyautogui.scroll(20)
                    cv2.putText(frame, "SCROLL UP", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                elif my > (h / 2) + 30: # මැදට වඩා පහළින් තිබේ නම්
                    pyautogui.scroll(-20)
                    cv2.putText(frame, "SCROLL DOWN", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("AI Mouse (Dev Branch)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()