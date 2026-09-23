# System Architecture

## System Pipeline

[Camera] → [Picamera2 Capture] → [Computer Vision Processing] → [Decision Logic] → [Output/Action]

Camera captures the image → Picamera2 processes the camera feed → Computer vision analyzes the image → The system decides what was detected → The result is displayed or an action is performed.

## FOV and Mounting Design

The camera will be mounted at a distance that keeps the entire target inside the camera's field of view.

Target size: 60 cm

Camera FOV: 70°

Mounting distance: 50 cm

Using the FOV formula:

FOV = 2 arctan(d / 2f)

The camera will be positioned approximately 50 cm from the target with a small margin around it. The camera will be angled slightly downward at approximately 10° to keep the target centered in the frame.
