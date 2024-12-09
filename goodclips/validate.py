import json
import os
import pandas as pd
from goodclips.download_clip import download_clip
from goodclips.deepsort_types import DeepsortOutput
from goodclips.ls_task import Data, get_clipevent_contact_ts
from goodclips.utils import (
    gen_deepsort_output,
    parse_deepsort_output,
    create_movement_by_frame,
)
import matplotlib.pyplot as plt


def load_deepsort_output(
    clip_id: str, deepsort_dir: str, df: pd.DataFrame
) -> tuple[DeepsortOutput, pd.Series]:
    file_path = os.path.join(deepsort_dir, f"{clip_id}.mp4.deepsort.json")
    clip_row = df[df["clipId"] == clip_id].iloc[0]
    if os.path.isfile(file_path):
        return (parse_deepsort_output(file_path), clip_row)
    else:
        raise FileNotFoundError(f"No deepsort output file found for clip ID: {clip_id}")


def create_movement_timeseries(deepsort_output: DeepsortOutput) -> pd.DataFrame:
    mv = create_movement_by_frame(deepsort_output)
    mv_df = pd.DataFrame(mv)
    mv_df["ts"] = pd.to_datetime(mv_df["ts"], unit="s")

    # Set the 'ts' column as the index and convert it to a datetime index
    mv_df.set_index("ts", inplace=True)

    # Resample the dataframe into 500ms intervals and calculate the mean movement for each interval
    mv_df_resampled = mv_df.resample("1000ms").sum()

    mv_df.reset_index(inplace=True)

    # Reset the index to get 'ts' back as a column
    mv_df_resampled.reset_index(inplace=True)
    return mv_df_resampled


def calculate_confidence_score(
    mv_df_resampled: pd.DataFrame, clipevent_ts: pd.Timestamp
) -> float:
    clipevent_ts += pd.Timedelta(seconds=0.5)
    # Find the index of the data point immediately previous to the clip event timestamp
    previous_index = mv_df_resampled[mv_df_resampled["ts"] < clipevent_ts].index[-1]

    max_movement = mv_df_resampled["movement"].max()
    max_movement_index = mv_df_resampled["movement"].idxmax()
    # Get the movement value at the previous index
    previous_value = mv_df_resampled.loc[previous_index, "movement"]

    # Initialize the confidence score
    confidence_score = 0.0
    # Check the next three data points
    max_proximate_movement = 0
    max_proximate_movement_index = 0
    for i in range(1, 4):
        next_index = previous_index + i
        if next_index < len(mv_df_resampled):
            next_value = mv_df_resampled.loc[next_index, "movement"]
            if next_value > previous_value:  # type: ignore
                confidence_score += 0.25
            previous_value = next_value
            if next_value > max_proximate_movement:  # type: ignore
                max_proximate_movement_index = next_index
                max_proximate_movement = next_value

    # Check if the maximum movement is within 10% of the overall maximum movement
    if max_proximate_movement_index <= max_movement_index and max_proximate_movement >= (max_movement * 0.9):  # type: ignore
        confidence_score += 0.25
    # or if the maximum is within the next three seconds after our local maximum
    elif max_movement_index >= max_proximate_movement_index and max_movement_index < max_proximate_movement_index + 4:  # type: ignore
        confidence_score += 0.25
    elif max_proximate_movement <= (max_movement * 0.6):
        confidence_score -= 0.25
    return confidence_score


def calc_confidence_for_clip(clip: Data, deepsort_output: DeepsortOutput) -> float:
    contact_event_ts = get_clipevent_contact_ts(clip)
    mv_by_frame = create_movement_timeseries(deepsort_output)
    clipevent_ts = pd.to_datetime(contact_event_ts, unit="s")
    confidence_score = calculate_confidence_score(mv_by_frame, clipevent_ts)
    return confidence_score


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Calculate confidence score for a clip"
    )
    parser.add_argument(
        "--clip_json",
        required=True,
        help="file containing clip json to calculate confidence for",
    )
    parser.add_argument(
        "--download_dir",
        default="ungitable/deepsort",
        help="Directory to save the downloaded clip",
    )
    args = parser.parse_args()

    try:
        with open(args.clip_json, "r") as file:
            data = json.load(file)
            clip_data = Data(**data)
        print("Clip ID:", clip_data.clipId)
        print("Downloading clip...")
        file_path = download_clip(clip_data, args.download_dir)
        print("Generating object tracking data...")
        deepsort_output = gen_deepsort_output(file_path)
        print("Calculating confidence score...")
        score = calc_confidence_for_clip(clip_data, deepsort_output)
        print(f"Confidence score for clip {clip_data.clipId}: {score}")
    except Exception as e:
        print(e)
    finally:
        os.remove(file_path)
