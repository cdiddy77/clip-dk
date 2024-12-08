from typing import TypedDict
from pydantic import BaseModel, Field


class DeepsortOutputFrame(BaseModel):
    bbox_xyxy: list[list[float]] = Field(
        ..., description="Bounding box coordinates in format [x1, y1, x2, y2]"
    )
    identities: list[int] = Field(
        ..., description="List of identities for each bounding box"
    )
    object_id: list[int] = Field(
        ..., description="List of object ids for each bounding box"
    )


class DeepsortOutput(BaseModel):
    frames: list[DeepsortOutputFrame] = Field(
        ..., description="List of frames with bounding boxes and identities"
    )
    object_id_names: list[str] = Field(..., description="List of object id names")


class MovementByFrame(TypedDict):
    ts: float
    movement: float


STANDARD_FPS = 30.0
LABELSTUDIO_FPS = 24.0
