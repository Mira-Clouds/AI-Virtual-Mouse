import cv2
import mediapipe as mp
import pyautogui
import numpy as np

# 1. Initialize MediaPipe and PyAutoGUI
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# Screen settings
screen_width, screen_height = pyautogui.size()
# Fail-safe disable කිරීමෙන් crash එක නවතී, නමුත් පරෙස්සමෙන් පාවිච්චි කරන්න
pyautogui.FAILSAFE = False 

# 2. Settings for Cursor & Smoothing
smooth_factor = 4  # මවුස් එකේ වේගය සහ smooth බව (3-7 අතර වෙනස් කරන්න)
margin_x, margin_y = 150, 150 
prev_x, prev_y = 0, 0
curr_x, curr_y = 0, 0

cap = cv2.VideoCapture(0)

print("AI Virtual Mouse started!")
print("1. Move Index Finger to move cursor.")
print("2. Touch Index & Thumb to Click.")
print("Press Q to quit.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # --- CURSOR MOVEMENT (Index Finger - Landmark 8) ---
            index_tip = hand_landmarks.landmark[8]
            ix = int(index_tip.x * w)
            iy = int(index_tip.y * h)

            # Mapping coordinates
            mapped_x = np.interp(ix, (margin_x, w - margin_x), (0, screen_width))
            mapped_y = np.interp(iy, (margin_y, h - margin_y), (0, screen_height))

            # Smoothing
            curr_x = prev_x + (mapped_x - prev_x) / smooth_factor
            curr_y = prev_y + (mapped_y - prev_y) / smooth_factor

            try:
                pyautogui.moveTo(curr_x, curr_y)
            except Exception:
                pass # Fail-safe crash වළක්වයි

            prev_x, prev_y = curr_x, curr_y

            # --- LEFT CLICK GESTURE (Thumb 4 and Index 8) ---
            thumb_tip = hand_landmarks.landmark[4]
            tx = int(thumb_tip.x * w)
            ty = int(thumb_tip.y * h)

            # ඇඟිලි දෙක අතර දුර මැනීම (Distance calculation)
            distance = np.hypot(ix - tx, iy - ty)

            # දුර 40 ට අඩු නම් Click එකක් ලෙස සලකයි (ඔයාගේ කැමරාව අනුව 30-50 වෙනස් කළ හැක)
            if distance < 40:
                pyautogui.click()
                pyautogui.sleep(0.2) # එක දිගට click වීම වැළැක්වීමට පොඩි විරාමයක්
                cv2.putText(frame, "CLICK", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                cv2.circle(frame, (ix, iy), 15, (0, 0, 255), cv2.FILLED)
            else:
                cv2.circle(frame, (ix, iy), 10, (0, 255, 0), cv2.FILLED)

    cv2.imshow("AI Virtual Mouse", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("AI Virtual Mouse stopped.")