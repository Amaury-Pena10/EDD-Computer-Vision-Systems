import cv2
import math
import mediapipe as mp
from picamera2 import Picamera2

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(
    main={"format": "XRGB8888", "size": (640, 480)}
))
picam2.start()


def calculate_angle(a, b, c):
    a, b, c = (a.x, a.y), (b.x, b.y), (c.x, c.y)
    radians = math.atan2(c[1] - b[1], c[0] - b[0]) - \
              math.atan2(a[1] - b[1], a[0] - b[0])
    angle = abs(math.degrees(radians))
    if angle > 180:
        angle = 360 - angle
    return angle


counter = 0
stage = None

try:
    while True:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            landmarks = results.pose_landmarks.landmark

            shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
            wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
            angle = calculate_angle(shoulder, elbow, wrist)

            h, w, _ = frame.shape
            elbow_px = (int(elbow.x * w), int(elbow.y * h))
            cv2.putText(frame, f"{int(angle)} deg", elbow_px,
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)

            if angle > 160:
                stage = "down"
            if angle < 60 and stage == "down":
                stage = "up"
                counter += 1

        cv2.rectangle(frame, (0, 0), (200, 80), (245, 117, 16), -1)
        cv2.putText(frame, "REPS", (15, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, str(counter), (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "STAGE", (100, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, str(stage), (100, 65), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow("Pose Angles", frame)
        if cv2.waitKey(20) & 0xFF == ord("q"):
            break

except KeyboardInterrupt:
    print("Interrupted by user")

finally:
    picam2.stop()
    cv2.destroyAllWindows()
