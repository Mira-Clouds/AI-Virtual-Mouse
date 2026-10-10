
import cv2

print("Starting webcam test...")

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    print("Camera 0 failed. Trying another camera mode...")
    camera.release()
    camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Could not open the webcam.")
    print("Check camera permissions and close other camera apps.")
    raise SystemExit(1)

print("Webcam opened successfully!")

while True:
    success, frame = camera.read()

    if not success:
        print("Could not read a frame.")
        break

    frame = cv2.flip(frame, 1)
    cv2.imshow("AI Virtual Mouse - Webcam Test", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
print("Webcam test finished.")
