from pydantic import BaseModel, HttpUrl
from typing import List, Optional


class Event(BaseModel):
    type: str
    isValid: bool
    ts: float


class VeloEvent(BaseModel):
    ts: float
    velocity: float
    exitVelo: int
    spinRate: int


class ClipData(BaseModel):
    J_teamGameId: str
    scoreGameId: str
    hvidId: str
    clipId: str
    teamId: str
    clipType: str
    clipStartTs: float
    clipStopTs: float
    clipDuration: float
    fileDownloadUrl: HttpUrl
    hvidStartOffset: float
    hvidEndOffset: float
    textDescriptionBrief: str
    textDescription: str
    events: List[Event]
    veloEventList: List[VeloEvent]


def clip_data_from_jsonl(file_path: str) -> List[ClipData]:
    result: List[ClipData] = []
    with open(file_path, "r") as f:
        for line in f:
            result.append(ClipData.model_validate_json(line))
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process clip data from a JSONL file.")
    parser.add_argument("--input", required=True, help="Path to the input JSONL file")
    args = parser.parse_args()

    data = clip_data_from_jsonl(args.input)
    print([x.clipId for x in data[:10]])
