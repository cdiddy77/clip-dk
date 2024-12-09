# clip-dk


open this directory in vscode. When prompted to reopen in devcontainer, do so. 

## to evaluate the confidence for a given clip:
 store the clip JSON, e.g. 
```json
{
    "clipId": "20rklLb793TvVuzD",
    "events": [
        {
            "ts": 24.928,
            "type": "contact",
            "isValid": true
        }
    ],
    "hvidId": "000LgP1I7vBuBkhD",
    "teamId": "OOZO-TmSh01-cyc-RHkcDbYSCpHB",
    "clipType": "ShortPlateAppearance",
    "clipStopTs": 1714521165.6,
    "clipStartTs": 1714521123.6,
    "scoreGameId": "GmSs01-be79489c-2235-4655-8100-3605952422af",
    "J_teamGameId": "GmSh01-GmSs01-be79489c-2235-4655-8100-3605952422af",
    "clipDuration": 42.0,
    "hvidEndOffset": 32.928,
    "veloEventList": [],
    "fileDownloadUrl": "https:\/\/f000.backblazeb2.com\/file\/shd-clip-23\/20240430ul__bot2__20rklLb793TvVuzD",
    "hvidStartOffset": 21.928,
    "textDescription": "Mason bot 2nd single vs Liberty Bell",
    "textDescriptionBrief": "single"
}
```
in a file, e.g. `ungitable/clip.json` and evaluate thus:

```sh
python goodclips/validate.py --clip_json ungitable/clip.json
```

## notebooks and utilities

- `notebooks/annotations.ipynb` : digs into analyzing clips
- `notebooks/measure_movement.ipynb` : a simple way to generate graps of movement

- `goodclips/gen_deepsorts.py` : builds the deepsort json files from the video files
