import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# ============================================================
# AI VIRTUAL MOUSE - smoother hand tracking
# ============================================================

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# Smaller margins allow more of the camera view to control the screen.
MARGIN_X = 60
MARGIN_Y = 45

# Higher = quicker cursor response; lower = smoother but slower.
SMOOTHING = 0.60

# Pinch thresholds, normalized to hand size.
LEFT_PINCH_ON = 0.32       # thumb + index = left click
LEFT_PINCH_OFF = 0.44
RIGHT_PINCH_ON = 0.32      # index + middle = right click
RIGHT_PINCH_OFF = 0.44
SCROLL_PINCH_ON = 0.35     # thumb + middle = scroll mode
SCROLL_PINCH_OFF = 0.47

CLICK_COOLDOWN = 0.35
SCROLL_PIXELS_PER_STEP = 16
SCROLL_DEADZONE = 2.0


def point_xy(landmark, width, height):
    return np.array([landmark.x * width, landmark.y * height], dtype=np.float32)


def distance(a, b):
    return float(np.linalg.norm(a - b))


def clamp(value, low, high):
    return max(low, min(value, high))


def main():
    # DirectShow is usually responsive on Windows; try the default backend if needed.
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap.release()
        cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        print("ERROR: Webcam could not be opened. Check camera permissions.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    previous_cursor = None
    left_was_pinched = False
    right_was_pinched = False
    scroll_was_pinched = False
    last_left_click = 0.0
    last_right_click = 0.0
    previous_scroll_y = None
    scroll_remainder = 0.0

    print("AI Virtual Mouse started")
    print("Move cursor: move index fingertip inside the rectangle")
    print("Left click: thumb + index finger pinch")
    print("Right click: index + middle finger pinch")
    print("Scroll: thumb + middle finger pinch, then move hand up/down")
    print("Press Q in the camera window to quit")
    print("Safety: move mouse to the top-left corner to stop mouse actions")

    try:
        with mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=1,
            min_detection_confidence=0.60,
            min_tracking_confidence=0.60
        ) as hands:
            while True:
                ok, frame = cap.read()
                if not ok:
                    print("ERROR: Cannot read webcam frame.")
                    break

                frame = cv2.flip(frame, 1)
                height, width = frame.shape[:2]

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb.flags.writeable = False
                results = hands.process(rgb)

                left_edge = min(MARGIN_X, width // 4)
                right_edge = max(left_edge + 1, width - MARGIN_X)
                top_edge = min(MARGIN_Y, height // 4)
                bottom_edge = max(top_edge + 1, height - MARGIN_Y)

                cv2.rectangle(
                    frame, (left_edge, top_edge), (right_edge, bottom_edge),
                    (180, 180, 180), 2
                )

                status = "Show your hand inside the box"
                status_color = (0, 200, 255)

                if results.multi_hand_landmarks:
                    hand = results.multi_hand_landmarks[0]
                    mp.solutions.drawing_utils.draw_landmarks(
                        frame, hand, mp.solutions.hands.HAND_CONNECTIONS
                    )
                    lm = hand.landmark

                    thumb = point_xy(lm[4], width, height)
                    index = point_xy(lm[8], width, height)
                    middle = point_xy(lm[12], width, height)
                    wrist = point_xy(lm[0], width, height)
                    middle_base = point_xy(lm[9], width, height)

                    # Normalize finger distances so gestures work at different camera distances.
                    hand_scale = max(distance(wrist, middle_base), 1.0)
                    left_distance = distance(thumb, index) / hand_scale
                    right_distance = distance(index, middle) / hand_scale
                    scroll_distance = distance(thumb, middle) / hand_scale

                    left_pinched = (
                        left_distance < LEFT_PINCH_OFF
                        if left_was_pinched else left_distance < LEFT_PINCH_ON
                    )
                    right_pinched = (
                        right_distance < RIGHT_PINCH_OFF
                        if right_was_pinched else right_distance < RIGHT_PINCH_ON
                    )
                    scroll_pinched = (
                        scroll_distance < SCROLL_PINCH_OFF
                        if scroll_was_pinched else scroll_distance < SCROLL_PINCH_ON
                    )

                    # Map index fingertip to the full screen with a small active margin.
                    target_x = np.interp(
                        clamp(index[0], left_edge, right_edge),
                        [left_edge, right_edge], [0, SCREEN_WIDTH - 1]
                    )
                    target_y = np.interp(
                        clamp(index[1], top_edge, bottom_edge),
                        [top_edge, bottom_edge], [0, SCREEN_HEIGHT - 1]
                    )

                    if previous_cursor is None:
                        smooth_x, smooth_y = target_x, target_y
                    else:
                        smooth_x = previous_cursor[0] + SMOOTHING * (
                            target_x - previous_cursor[0]
                        )
                        smooth_y = previous_cursor[1] + SMOOTHING * (
                            target_y - previous_cursor[1]
                        )

                    # Cursor keeps moving while clicking; pause it only for scroll mode.
                    if not scroll_pinched:
                        pyautogui.moveTo(int(smooth_x), int(smooth_y), _pause=False)
                        status = "TRACKING - Move index finger"
                        status_color = (0, 220, 0)
                    else:
                        status = "SCROLL - Move hand UP/DOWN"
                        status_color = (0, 220, 255)

                    now = time.monotonic()

                    # Click only once when a pinch starts, not on every video frame.
                    if (
                        left_pinched and not left_was_pinched
                        and now - last_left_click >= CLICK_COOLDOWN
                    ):
                        pyautogui.click()
                        last_left_click = now
                        status = "LEFT CLICK"
                        status_color = (0, 255, 0)

                    # Right-click uses index + middle finger, separate from scroll gesture.
                    if (
                        right_pinched and not right_was_pinched
                        and not scroll_pinched
                        and now - last_right_click >= CLICK_COOLDOWN
                    ):
                        pyautogui.rightClick()
                        last_right_click = now
                        status = "RIGHT CLICK"
                        status_color = (0, 0, 255)

                    # Scroll uses thumb + middle finger pinch, then hand movement.
                    if scroll_pinched:
                        current_y = float(middle[1])
                        if not scroll_was_pinched or previous_scroll_y is None:
                            previous_scroll_y = current_y
                            scroll_remainder = 0.0
                        else:
                            delta_y = previous_scroll_y - current_y
                            if abs(delta_y) >= SCROLL_DEADZONE:
                                scroll_remainder += delta_y
                                steps = int(scroll_remainder / SCROLL_PIXELS_PER_STEP)
                                steps = int(clamp(steps, -6, 6))
                                if steps != 0:
                                    pyautogui.scroll(steps)
                                    scroll_remainder -= steps * SCROLL_PIXELS_PER_STEP
                            previous_scroll_y = current_y
                    else:
                        previous_scroll_y = None
                        scroll_remainder = 0.0

                    left_was_pinched = left_pinched
                    right_was_pinched = right_pinched
                    scroll_was_pinched = scroll_pinched
                    previous_cursor = (smooth_x, smooth_y)

                    for p in (thumb, index, middle):
                        cv2.circle(frame, tuple(p.astype(int)), 7, (255, 180, 0), -1)

                    cv2.putText(
                        frame,
                        f"L:{left_distance:.2f} R:{right_distance:.2f} S:{scroll_distance:.2f}",
                        (10, height - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                        (255, 255, 255), 2
                    )
                else:
                    previous_cursor = None
                    left_was_pinched = False
                    right_was_pinched = False
                    scroll_was_pinched = False
                    previous_scroll_y = None
                    scroll_remainder = 0.0

                cv2.putText(
                    frame, status, (20, 38), cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, status_color, 2
                )
                cv2.putText(
                    frame, "Q: Quit | Keep index fingertip inside rectangle",
                    (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
                )

                cv2.imshow("AI Virtual Mouse", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    except pyautogui.FailSafeException:
        print("PyAutoGUI safety stop triggered (mouse reached top-left corner).")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("AI Virtual Mouse stopped.")


if __name__ == "__main__":
    main()
