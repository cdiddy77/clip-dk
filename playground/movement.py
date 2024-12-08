import cv2
import numpy as np
from ultralytics import YOLO
import matplotlib.pyplot as plt

# Load YOLOv8 model
model = YOLO("yolov8n.pt")  # Adjust the YOLO model variant as needed

# Open video file
video_path = "ungitable/2cKVta2pHP2Eq2ts.mp4"
cap = cv2.VideoCapture(video_path)

# Ensure video is opened
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Parameters to keep track of movement
previous_frame = None
movement_series = []

while True:
    ret, frame = cap.read()
    if not ret:
        break  # End of video

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect objects in the current frame
    results = model(frame)

    # Measure movement between frames
    if previous_frame is not None:
        # Calculate absolute difference between the current frame and the previous frame
        frame_diff = cv2.absdiff(previous_frame, gray)

        # Threshold the difference to binarize
        _, thresh = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)

        # Calculate the amount of movement (sum of non-zero pixels)
        movement = np.sum(thresh) / 255
        movement_series.append(movement)

    # Update the previous frame
    previous_frame = gray

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the video capture and close windows
cap.release()
cv2.destroyAllWindows()

# Plot the movement time series
plt.plot(movement_series)
plt.xlabel("Frame")
plt.ylabel("Movement")
plt.title("Movement Time Series")
plt.show()
