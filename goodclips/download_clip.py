import requests

from goodclips.ls_task import Data, parse_mainjson_list


def download_clip(data: Data, video_path):
    response = requests.get(data.fileDownloadUrl)
    file_path = f"{video_path}/{data.clipId}.mp4"
    with open(file_path, "wb") as file:
        file.write(response.content)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process clip data from a JSONL file.")
    parser.add_argument("--id", required=True, help="ID of the clip to download")
    parser.add_argument(
        "--dir",
        default="ungitable/deepsort",
        help="Directory to save the downloaded clip",
    )
    args = parser.parse_args()
    anno_data = parse_mainjson_list(
        "ungitable/project-1-at-2024-12-08-00-58-c2cfaffe.json"
    )
    data = [t.data for t in anno_data if t.data.clipId == args.id]
    if len(data) == 0:
        print(f"Clip with ID {args.id} not found in the data")
    elif len(data) > 1:
        print(f"Multiple clips with ID {args.id} found in the data")
    else:
        download_clip(data[0], args.dir)
