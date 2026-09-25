# final_project.py - Build Sprint 2
# face_recognition and output logic. 
import cv2
import face_recognition
import os
import RPi.GPIO as GPIO
from picamera2 import Picamera2

KNOWN_FACES_DIR = os.path.expanduser(
    "~/EDD-Computer-Vision-Systems/cv_project/images/known_faces"
)

# -----------------------------
# LED GPIO PIN SETUP
# -----------------------------
GREEN_LED = 17
RED_LED = 27
ORANGE_LED = 22

GPIO.setmode(GPIO.BCM)

GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(ORANGE_LED, GPIO.OUT)

# Turn all LEDs off initially
GPIO.output(GREEN_LED, GPIO.LOW)
GPIO.output(RED_LED, GPIO.LOW)
GPIO.output(ORANGE_LED, GPIO.LOW)


# -----------------------------
# LOAD KNOWN FACES
# -----------------------------
known_encodings = []
known_names = []

for filename in os.listdir(KNOWN_FACES_DIR):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):

        path = os.path.join(KNOWN_FACES_DIR, filename)

        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)

        if encodings:
            known_encodings.append(encodings[0])

            name = os.path.splitext(filename)[0].replace("_", " ").title()
            known_names.append(name)

print(f"Loaded {len(known_names)} known face(s): {known_names}")


# -----------------------------
# START CAMERA
# -----------------------------
picam2 = Picamera2()

picam2.configure(
    picam2.create_preview_configuration(
        main={
            "format": "XRGB8888",
            "size": (640, 480)
        }
    )
)

picam2.start()


try:

    while True:

        # Capture frame
        frame = picam2.capture_array()

        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGRA2BGR
        )

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # Make image smaller for faster recognition
        small_frame = cv2.resize(
            rgb_frame,
            (0, 0),
            fx=0.5,
            fy=0.5
        )

        # Find faces
        face_locations = face_recognition.face_locations(
            small_frame
        )

        face_encodings = face_recognition.face_encodings(
            small_frame,
            face_locations
        )

        # Track whether known/unknown faces are present
        known_face_detected = False
        unknown_face_detected = False


        # -----------------------------
        # PROCESS EACH FACE
        # -----------------------------
        for (top, right, bottom, left), face_encoding in zip(
            face_locations,
            face_encodings
        ):

            matches = face_recognition.compare_faces(
                known_encodings,
                face_encoding,
                tolerance=0.6
            )

            name = "Unknown"

            if True in matches:
                name = known_names[matches.index(True)]
                known_face_detected = True

            else:
                unknown_face_detected = True


            # Scale coordinates back to original image
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2


            # -----------------------------
            # DRAW FACE BOX
            # -----------------------------
            if name == "Unknown":
                color = (0, 0, 255)       # Red

            else:
                color = (0, 255, 0)       # Green


            cv2.rectangle(
                frame,
                (left, top),
                (right, bottom),
                color,
                2
            )


            cv2.putText(
                frame,
                name,
                (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2,
                cv2.LINE_AA
            )


        # -----------------------------
        # CONTROL LEDs
        # -----------------------------

        # Turn all LEDs off first
        GPIO.output(GREEN_LED, GPIO.LOW)
        GPIO.output(RED_LED, GPIO.LOW)
        GPIO.output(ORANGE_LED, GPIO.LOW)


        # Known AND unknown face
        if known_face_detected and unknown_face_detected:

            GPIO.output(ORANGE_LED, GPIO.HIGH)


        # Only known face(s)
        elif known_face_detected:

            GPIO.output(GREEN_LED, GPIO.HIGH)


        # Only unknown face(s)
        elif unknown_face_detected:

            GPIO.output(RED_LED, GPIO.HIGH)


        # No faces detected
        else:

            GPIO.output(GREEN_LED, GPIO.LOW)
            GPIO.output(RED_LED, GPIO.LOW)
            GPIO.output(ORANGE_LED, GPIO.LOW)


        # -----------------------------
        # DISPLAY CAMERA
        # -----------------------------
        cv2.imshow(
            "Face Recognition",
            frame
        )


        # Press Q to quit
        if cv2.waitKey(20) & 0xFF == ord("q"):
            break


except KeyboardInterrupt:

    print("Interrupted by user")


finally:

    # Turn LEDs off
    GPIO.output(GREEN_LED, GPIO.LOW)
    GPIO.output(RED_LED, GPIO.LOW)
    GPIO.output(ORANGE_LED, GPIO.LOW)

    # Clean up GPIO
    GPIO.cleanup()

    # Stop camera
    picam2.stop()

    cv2.destroyAllWindows()
