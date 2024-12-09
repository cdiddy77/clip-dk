from goodclips.ls_task import Annotation, Data, parse_mainjson_list
import os
import requests

from goodclips.utils import gen_deepsort_output


def gen_deepsort(video_path: str, data: Data):
    deepsort_output_file = f"{video_path}/{data.clipId}.mp4.deepsort.json"

    if os.path.exists(deepsort_output_file):
        print(f"Deepsort output file for data[{data.clipId}] already exists")
        return

    # Download the file
    response = requests.get(data.fileDownloadUrl)
    file_path = f"{video_path}/{data.clipId}.mp4"
    with open(file_path, "wb") as file:
        file.write(response.content)

    # Generate deepsort output
    deepsort_output = gen_deepsort_output(file_path)
    # Delete the video file
    os.remove(file_path)
    # Serialize deepsort output to a file
    with open(deepsort_output_file, "w") as file:
        file.write(deepsort_output.model_dump_json(indent=2))


anno_data = parse_mainjson_list("ungitable/project-1-at-2024-12-08-00-58-c2cfaffe.json")

annos: list[tuple[Annotation, Data]] = [
    (t.annotations[0], t.data) for t in anno_data if len(t.annotations) > 0
]

count = 0
for anno, data in annos:
    try:
        gen_deepsort("ungitable/deepsort", data)
        print(f"******* [{count}] Processed data[{data.clipId}]")
    except Exception as e:
        print(f"******* [{count}] ERROR processing data[{data.clipId}]: {e}")
    count += 1
