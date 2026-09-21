from picamera2 import Picamera2
import cv2
import os

SAVE_PATH = "../images/known_faces/amaury_pena.jpg"

os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)

picam2 = Picamera2()
picam2.configure(
    picam2.create_preview_configuration(
        main={"format": "XRGB8888", "size": (640, 480)}
    )
)
picam2.start()

print("Live camera started.")
print("Press 's' to save the photo.")
print("Press 'q' to quit without saving.")

while True:
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    cv2.imshow("Capture Known Face", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("s"):
        cv2.imwrite(SAVE_PATH, frame)
        print(f"Photo saved to: {SAVE_PATH}")
        break

    elif key == ord("q"):
        print("Quit without saving.")
        break

picam2.stop()
cv2.destroyAllWindows()
