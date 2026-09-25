# final_project.py - Build Sprint 2
# Core detection/tracking logic only. Output/action logic comes in
```python
import cv2
import face_recognition
import os
import RPi.GPIO as GPIO
from picamera2 import Picamera2


# ============================================================
# SETTINGS
# ============================================================

KNOWN_FACES_DIR = os.path.expanduser(
    "~/EDD-Computer-Vision-Systems/cv_project/images/known_faces"
)

MAX_FACES = 2

# Recognition tolerance
# Lower = stricter
# Higher = more forgiving
TOLERANCE = 0.6


# ============================================================
# LED GPIO PINS
# ============================================================

GREEN_LED = 17
RED_LED = 27
ORANGE_LED = 22


GPIO.setmode(GPIO.BCM)

GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(ORANGE_LED, GPIO.OUT)


def turn_off_leds():
    GPIO.output(GREEN_LED, GPIO.LOW)
    GPIO.output(RED_LED, GPIO.LOW)
    GPIO.output(ORANGE_LED, GPIO.LOW)


turn_off_leds()


# ============================================================
# LOAD KNOWN FACES
# ============================================================

known_encodings = []
known_names = []


print("\nLoading known faces...\n")


for filename in sorted(os.listdir(KNOWN_FACES_DIR)):

    if not filename.lower().endswith(
        (".jpg", ".jpeg", ".png")
    ):
        continue

    path = os.path.join(
        KNOWN_FACES_DIR,
        filename
    )

    try:

        image = face_recognition.load_image_file(path)

        # Find every face in the known image
        encodings = face_recognition.face_encodings(image)

        if len(encodings) == 0:

            print(
                f"WARNING: No face found in {filename}"
            )

            continue

        if len(encodings) > 1:

            print(
                f"WARNING: Multiple faces found in {filename}. "
                f"Using the first face."
            )

        # Use the first face in the image
        encoding = encodings[0]

        # Convert filename into person's name
        name = os.path.splitext(filename)[0]
        name = name.replace("_", " ")
        name = name.replace("-", " ")
        name = name.title()

        known_encodings.append(encoding)
        known_names.append(name)

        print(
            f"Loaded: {name} <- {filename}"
        )

    except Exception as e:

        print(
            f"ERROR loading {filename}: {e}"
        )


print("\n--------------------------------")
print(f"Known faces loaded: {len(known_names)}")

for name in known_names:
    print(f"  - {name}")

print("--------------------------------\n")


# ============================================================
# MAKE SURE WE HAVE A KNOWN FACE
# ============================================================

if len(known_encodings) == 0:

    print(
        "ERROR: No usable known faces were found."
    )

    GPIO.cleanup()
    exit()


# ============================================================
# START CAMERA
# ============================================================

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


# ============================================================
# MAIN LOOP
# ============================================================

try:

    while True:

        # ----------------------------------------------------
        # CAPTURE FRAME
        # ----------------------------------------------------

        frame = picam2.capture_array()

        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGRA2BGR
        )

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )


        # ----------------------------------------------------
        # RESIZE FOR FASTER PROCESSING
        # ----------------------------------------------------

        small_frame = cv2.resize(
            rgb_frame,
            (0, 0),
            fx=0.5,
            fy=0.5
        )


        # ----------------------------------------------------
        # FIND FACES
        # ----------------------------------------------------

        face_locations = face_recognition.face_locations(
            small_frame,
            model="hog"
        )


        # Only process up to 2 faces
        face_locations = face_locations[:MAX_FACES]


        # ----------------------------------------------------
        # CREATE FACE ENCODINGS
        # ----------------------------------------------------

        face_encodings = face_recognition.face_encodings(
            small_frame,
            face_locations
        )


        known_face_detected = False
        unknown_face_detected = False


        # ----------------------------------------------------
        # PROCESS EACH DETECTED FACE
        # ----------------------------------------------------

        for face_location, face_encoding in zip(
            face_locations,
            face_encodings
        ):

            top, right, bottom, left = face_location


            # =================================================
            # FIND CLOSEST KNOWN FACE
            # =================================================

            face_distances = face_recognition.face_distance(
                known_encodings,
                face_encoding
            )


            best_match_index = face_distances.argmin()

            best_distance = face_distances[
                best_match_index
            ]


            # Default to unknown
            name = "Unknown"


            # -------------------------------------------------
            # CHECK IF CLOSEST FACE IS CLOSE ENOUGH
            # -------------------------------------------------

            if best_distance <= TOLERANCE:

                name = known_names[
                    best_match_index
                ]

                known_face_detected = True

            else:

                unknown_face_detected = True


            # =================================================
            # SCALE COORDINATES
            # =================================================

            top *= 2
            right *= 2
            bottom *= 2
            left *= 2


            # =================================================
            # COLORS
            # =================================================

            if name == "Unknown":

                # Red
                color = (0, 0, 255)

            else:

                # Green
                color = (0, 255, 0)


            # =================================================
            # DRAW FACE BOX
            # =================================================

            cv2.rectangle(
                frame,
                (left, top),
                (right, bottom),
                color,
                2
            )


            # =================================================
            # DISPLAY NAME
            # =================================================

            cv2.putText(
                frame,
                name,
                (left, top - 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2,
                cv2.LINE_AA
            )


            # =================================================
            # DISPLAY CONFIDENCE/DISTANCE
            # =================================================

            cv2.putText(
                frame,
                f"Distance: {best_distance:.2f}",
                (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1,
                cv2.LINE_AA
            )


        # ====================================================
        # LED CONTROL
        # ====================================================

        turn_off_leds()


        # ----------------------------------------------------
        # KNOWN + UNKNOWN
        # ----------------------------------------------------

        if known_face_detected and unknown_face_detected:

            GPIO.output(
                ORANGE_LED,
                GPIO.HIGH
            )


        # ----------------------------------------------------
        # ONLY KNOWN
        # ----------------------------------------------------

        elif known_face_detected:

            GPIO.output(
                GREEN_LED,
                GPIO.HIGH
            )


        # ----------------------------------------------------
        # ONLY UNKNOWN
        # ----------------------------------------------------

        elif unknown_face_detected:

            GPIO.output(
                RED_LED,
                GPIO.HIGH
            )


        # ----------------------------------------------------
        # NO FACES
        # ----------------------------------------------------

        else:

            turn_off_leds()


        # ====================================================
        # DISPLAY FACE COUNT
        # ====================================================

        cv2.putText(
            frame,
            f"Faces: {len(face_locations)}/{MAX_FACES}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )


        # ====================================================
        # DISPLAY CAMERA
        # ====================================================

        cv2.imshow(
            "Face Recognition",
            frame
        )


        # ====================================================
        # QUIT WITH Q
        # ====================================================

        if cv2.waitKey(20) & 0xFF == ord("q"):

            break


# ============================================================
# CLEANUP
# ============================================================

except KeyboardInterrupt:

    print("\nProgram stopped.")


finally:

    turn_off_leds()

    GPIO.cleanup()

    picam2.stop()

    cv2.destroyAllWindows()

    print("GPIO and camera cleaned up.")
```
