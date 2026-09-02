import cv2

# Load an image from disk
img = cv2.imread('/home/pi/cv_project/images/test_full.jpg')

# Print shape: (height, width, channels)
print(f"Image shape: {img.shape}")
print(f"Data type: {img.dtype}")

# Display it (requires a monitor or VNC — if headless, skip to saving)
cv2.imshow('My Image', img)
cv2.waitKey(0)         # Wait for any key press
cv2.destroyAllWindows()
