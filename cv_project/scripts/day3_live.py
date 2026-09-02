import cv2
from picamera2 import Picamera2

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(
    main={"format": 'XRGB8888', "size": (640, 480)}
))
picam2.start()

try:
    while True:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)  # convert to OpenCV's format
        small = cv2.resize(frame, (320, 240))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (15, 15), 0)
        # Rectangle: (image, top-left corner, bottom-right corner, color BGR, thickness)
        cv2.rectangle(frame, (50, 50), (200, 200), (0, 255, 0), 2)

# Circle: (image, center, radius, color BGR, thickness)
        cv2.circle(frame, (320, 240), 30, (255, 0, 0), 3)

# Text: (image, text, origin, font, scale, color BGR, thickness)
        cv2.putText(frame, 'Hello CV!', (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        # --- All processing happens here ---
        cv2.imshow('Live Feed', frame)

        # Press 'q' (with the window focused) to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Interrupted by user")

finally:
    picam2.stop()
    cv2.destroyAllWindows()
