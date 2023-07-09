# bbkiller
The /b-Level Tools (TM) presents.

The Subj finds frames with bounding boxes, extracts those frames, repairs them using the CliDrop API, encodes output videos without bounding boxes. When using The Subj, one should set the environmental variable `API_TOKEN`. The token is obtained from [here](https://clipdrop.co). Colors of bounding boxes being removed are set in `cfg.py`.

## Use Example

```
mkdir -p data/video_folder data/frames_folder data/out_folder
cp YOUR_DATA/*.mp4 data/video_folder
python app.py extract video_folder frames_folder
python app.py repair frames_folder
python app.py encode viedo_folder frames_folder out_folder
cp data/out_folder/*.mp4 OUTPUT_DATA
```