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
