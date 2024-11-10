import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image
import tempfile
import time

# Initialize the YOLOv8 model
model = YOLO("yolov8n.pt")  # Use the appropriate YOLOv8 model weights

# Set Streamlit layout
st.title("Video Object Detection with YOLOv8")
st.sidebar.title("Upload and Play Video")

# Upload video file
video_file = st.sidebar.file_uploader("Choose a video...", type=["mp4", "avi", "mov"])


def detect_and_render_frame(model, frame, video_frame_placeholder):
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
    video_frame_placeholder.image(frame, channels="BGR", caption="Detected Objects")


if video_file is not None:
    temp_file = tempfile.NamedTemporaryFile(delete=False)  # Don't delete immediately
    temp_file.write(video_file.read())
    temp_file.close()  # Load the video using OpenCV
    video = cv2.VideoCapture(temp_file.name)

    fps = int(video.get(cv2.CAP_PROP_FPS))
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    st.sidebar.write(f"Frames per second (FPS): {fps}")
    st.sidebar.write(f"Total frames: {total_frames}")
    st.sidebar.write(f"Duration (seconds): {duration:.2f}")

    # Initialize Streamlit slider for frame navigation
    frame_idx = st.slider("Frame", 0, total_frames - 1, 0)
    video_frame_placeholder = st.empty()

    # Play/Pause functionality
    is_playing = st.sidebar.button("Play/Pause")
    if "playing" not in st.session_state:
        st.session_state.playing = False  # Initialize play state

    # Toggle play/pause when the button is clicked
    if is_playing:
        st.session_state.playing = not st.session_state.playing

    # Set video to the frame at the slider position
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    success, frame = video.read()

    if st.session_state.playing:
        while st.session_state.playing:
            # Calculate the frame to show based on FPS and time elapsed
            current_time = frame_idx / fps
            frame_idx += fps  # Move forward 1 second in the video

            # Ensure the frame index doesn't go beyond the total frame count
            if frame_idx >= total_frames:
                frame_idx = 0
                st.session_state.playing = False  # Stop when video reaches the end
                break

            # Set the video to the next frame
            video.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            success, frame = video.read()

            if success:
                # Display the current frame
                # st.image(frame, channels="BGR")
                detect_and_render_frame(model, frame, video_frame_placeholder)
            else:
                st.write("Unable to read frame from video.")
                break

            # Sleep to simulate real-time playback
            time.sleep(1)
    else:
        detect_and_render_frame(model, frame, video_frame_placeholder)

    # Release the video when done
    video.release()
else:
    st.write("Please upload a video file to start.")
