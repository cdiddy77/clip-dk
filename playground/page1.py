import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image

# Initialize the YOLOv8 model
model = YOLO("yolov8n.pt")  # Use the appropriate YOLOv8 model weights

# Set Streamlit layout
st.title("Video Object Detection with YOLOv8")
st.sidebar.title("Upload and Play Video")

# Upload video file
video_file = st.sidebar.file_uploader("Choose a video...", type=["mp4", "avi", "mov"])

if video_file is not None:
    # Load the video using OpenCV
    video = cv2.VideoCapture(video_file.name)

    # Retrieve video properties
    fps = int(video.get(cv2.CAP_PROP_FPS))
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    st.sidebar.write(f"Frames per second (FPS): {fps}")
    st.sidebar.write(f"Total frames: {total_frames}")

    # Initialize Streamlit slider for frame navigation
    frame_idx = st.slider("Frame", 0, total_frames - 1, 0)

    # Set video to the frame at the slider position
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    success, frame = video.read()

    if success:
        # Display the current frame
        st.image(frame, channels="BGR")

        # Button to detect objects on the current frame
        if st.button("Detect Objects"):
            # Perform object detection on the current frame
            results = model(frame)

            # Draw rectangles around detected objects
            for box in results[0].boxes:
                x1, y1, x2, y2 = box.xyxy[0]  # Coordinates of the box
                conf = box.conf[0]  # Confidence
                cls = box.cls[0]  # Class

                # Draw rectangle and label on frame
                frame = cv2.rectangle(
                    frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2
                )
                frame = cv2.putText(
                    frame,
                    f"{model.names[int(cls)]} {conf:.2f}",
                    (int(x1), int(y1) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2,
                )

            # Display the annotated frame
            st.image(frame, channels="BGR", caption="Detected Objects")

    else:
        st.write("Unable to read frame from video.")

    # Release the video when done
    video.release()
else:
    st.write("Please upload a video file to start.")
