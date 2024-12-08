import math
import cv2
from ultralytics import YOLO
import os

from goodclips.types import DeepsortOutput, DeepsortOutputFrame


def intersection_area(boxA: list[float], boxB: list[float]) -> float:
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    # compute the area of intersection rectangle
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

    # return the intersection area
    return interArea


def area(box: list[float]) -> float:
    return (box[2] - box[0]) * (box[3] - box[1])


def baseline_midpoint(bbox: list[float]) -> list[float]:
    x1, y1, x2, y2 = bbox
    return [(x1 + x2) / 2, max(y1, y2)]


def distance_between_points(p1: list[float], p2: list[float]) -> float:
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def vector_magnitude(v: list[float]) -> float:
    return math.sqrt(v[0] ** 2 + v[1] ** 2)


def vector_between_points(p1: list[float], p2: list[float]) -> list[float]:
    return [p2[0] - p1[0], p2[1] - p1[1]]


def distance_between_bboxes(bbox1: list[float], bbox2: list[float]) -> float:
    return distance_between_points(baseline_midpoint(bbox1), baseline_midpoint(bbox2))


def vector_between_bboxes(bbox1: list[float], bbox2: list[float]) -> list[float]:
    return vector_between_points(baseline_midpoint(bbox1), baseline_midpoint(bbox2))


def gen_deepsort_output(video_file: str, max_frames: int = -1) -> DeepsortOutput:
    model = YOLO("yolov8n.pt")  # Adjust the YOLO model variant as needed
    cap = cv2.VideoCapture(video_file)
    frames: list[DeepsortOutputFrame] = []
    object_id_names = []
    cur_frame = 0
    while cap.isOpened() and (max_frames == -1 or cur_frame < max_frames):
        # Read a frame from the video
        success, frame = cap.read()
        cur_frame += 1
        if success:
            results = model.track(frame, persist=True)

            assert results[0].boxes is not None
            if not object_id_names:
                object_id_names = results[0].names.values()
            boxes = results[0].boxes.xyxy.cpu().tolist()  # type: ignore
            identities = results[0].boxes.id.cpu().tolist()  # type: ignore
            names = [int(x.cls) for x in results[0].boxes]
            frame = DeepsortOutputFrame(
                bbox_xyxy=boxes,
                identities=identities,
                object_id=names,
            )
            frames.append(frame)
        else:
            break
    return DeepsortOutput(frames=frames, object_id_names=object_id_names)


def measure_movement(
    deepsort_output: DeepsortOutput,
    frame_index: int,
) -> float:
    if frame_index == 0:
        return 0.0
    frame = deepsort_output.frames[frame_index]
    prev_frame = deepsort_output.frames[frame_index - 1]

    # for each of the identities in identity, create a map of the index
    # of the identity in this frame to the index of the identity in the previous frame
    identity_map = {}
    for i, identity in enumerate(frame.identities):
        if identity not in identity_map:
            identity_map[identity] = []
        identity_map[identity].append(i)
    prev_identity_map = {}
    for i, identity in enumerate(prev_frame.identities):
        if identity not in prev_identity_map:
            prev_identity_map[identity] = []
        prev_identity_map[identity].append(i)

    movement = 0.0

    # not_in_prev_frame = set(identity_map.keys()) - set(prev_identity_map.keys())
    # not_in_this_frame = set(prev_identity_map.keys()) - set(identity_map.keys())

    for identity in identity_map:
        # for now we don't consider identities that are not in the previous frame
        # nor do we consider identities that were in the previous frame but not in this frame
        if identity not in prev_identity_map:
            continue
        for i, j in zip(identity_map[identity], prev_identity_map[identity]):
            # the z factor is 1 if the area of the bounding box is the same
            # else it is 1 + the difference in area divided by the area of the current bounding box
            z_factor = 1 + (
                abs(area(frame.bbox_xyxy[i]) - area(prev_frame.bbox_xyxy[j]))
                / area(frame.bbox_xyxy[i])
            )
            movement += (
                distance_between_bboxes(frame.bbox_xyxy[i], prev_frame.bbox_xyxy[j])
                * z_factor
            )
            # we could also consider the size or shape of the box
            # changing over time.

    return movement


if __name__ == "__main__":
    result = gen_deepsort_output("ungitable/2cKVta2pHP2Eq2ts.mp4", max_frames=10)
    print(result)
