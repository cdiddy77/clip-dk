from typing import List, Optional, Dict, Any, Union, cast
from pydantic import BaseModel
import json

from goodclips.deepsort_types import LABELSTUDIO_FPS


class ChoiceValue(BaseModel):
    choices: List[str]


class RectangleSequence(BaseModel):
    x: float
    y: float
    time: float
    frame: int
    width: float
    height: float
    enabled: bool
    rotation: int


class VideoRectangleValue(BaseModel):
    labels: Optional[List[str]] = None
    duration: float
    sequence: List[RectangleSequence]
    framesCount: int


class TimelineRange(BaseModel):
    start: int
    end: int


class TimelineValue(BaseModel):
    ranges: Optional[List[TimelineRange]] = None
    timelinelabels: List[str]


class AnnotationResult(BaseModel):
    id: str
    type: str
    value: Union[ChoiceValue, VideoRectangleValue, TimelineValue]
    # value: Any  # Can be ChoiceValue, VideoRectangleValue, or TimelineValue
    origin: str
    to_name: str
    from_name: str


class Annotation(BaseModel):
    id: int
    completed_by: int
    result: List[AnnotationResult]
    was_cancelled: bool
    ground_truth: bool
    created_at: str
    updated_at: str
    draft_created_at: Optional[str]
    lead_time: float
    prediction: Dict[str, Any]
    result_count: int
    unique_id: str
    import_id: Optional[str]
    last_action: Optional[str]
    task: int
    project: int
    updated_by: int
    parent_prediction: Optional[str]
    parent_annotation: Optional[str]
    last_created_by: Optional[str]


class Event(BaseModel):
    ts: float
    type: str
    isValid: bool


class Data(BaseModel):
    clipId: str
    events: List[Event]
    hvidId: str
    teamId: str
    clipType: str
    clipStopTs: float
    clipStartTs: float
    scoreGameId: str
    J_teamGameId: str
    clipDuration: float
    hvidEndOffset: float
    veloEventList: List[Any]
    fileDownloadUrl: str
    hvidStartOffset: float
    textDescription: str
    textDescriptionBrief: str


class LsTask(BaseModel):
    id: int
    annotations: List[Annotation]
    file_upload: str
    drafts: List[Any]
    predictions: List[Any]
    data: Data
    meta: Dict[str, Any]
    created_at: str
    updated_at: str
    inner_id: int
    total_annotations: int
    cancelled_annotations: int
    total_predictions: int
    comment_count: int
    unresolved_comment_count: int
    last_comment_updated_at: Optional[str]
    project: int
    updated_by: int
    comment_authors: List[Any]


# Function to parse a list of MainJSON objects from a JSON file
def parse_mainjson_list(file_path: str) -> List[LsTask]:
    with open(file_path, "r") as file:
        data = json.load(file)
    return [LsTask(**item) for item in data]


# oddly, label studio seems to have 24 fps, despite we know the video is actually 30 fps


def get_ballinplay_ts(annos: list[Annotation]) -> float:
    for anno in annos:
        for result in anno.result:
            if result.type == "timelinelabels" and isinstance(
                result.value, TimelineValue
            ):
                if (
                    result.value.timelinelabels[0] == "Ball-in-play Contact"
                    and result.value.ranges
                    and len(result.value.ranges) > 0
                ):
                    return float(result.value.ranges[0].start) / LABELSTUDIO_FPS
    return -1.0


def get_clipevent_contact_ts(clip: Data) -> float:
    for event in clip.events:
        if event.type == "contact":
            return event.ts
    return -1.0
