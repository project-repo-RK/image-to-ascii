# Image to ASCII

A machine-learning project that rebuilds an image using ASCII character tiles.
A trained SGD classifier predicts a character for each 10×10 tile. The local
webpage shows the original image and converted PNG side by side.

The model works considerably better with high-resolution images. The converter
keeps the input resolution, apart from the notebook's padding step.

## Setup and use

Use Python 3.11 or 3.12. Extract the ZIP and open a terminal in this folder.

```bash
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Install the dependencies and start the local server:

```bash
python -m pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000** in a browser. Click **Upload image**, then **Convert**.
Use **Download PNG** to save the result. Press Ctrl+C in the terminal to stop.
The Python server must be running; opening the HTML file directly will not work.

No GPU, retraining, font installation, or API key is needed. Installing dependencies
requires internet access; conversion runs locally. Uploads are kept in memory,
not saved to disk. The page accepts PNG, JPEG, WebP, and BMP images up to 32 MB
and 24 megapixels. Large images take longer to convert.

If PowerShell blocks activation, use `.venv\Scripts\python.exe` instead of `python`
for installation and startup. If port 5000 is occupied, change it in `app.py`.

## Standalone conversion

```bash
python converter.py path/to/input.jpg path/to/output.png
```

## Project files

| File or folder | Purpose |
| --- | --- |
| `converter.py` | Load the model, prepare the input, predict tiles, and assemble the output |
| `app.py` | Serve the local webpage and handle image uploads |
| `templates/`, `static/` | Page layout, styling, and upload controls |
| `models/sgd_ascii_model.joblib` | Original trained model, unchanged |
| `assets/ascii_images_shrunk/` | Original 10×10 PNGs used by the converter |
| `assets/ascii_images/` | Original 20×20 PNGs used by the earlier notebook experiments |
| `notebooks/model_training_and_development.ipynb` | Model training and development history |
| `requirements*.txt` | Application and optional notebook dependencies |

## How conversion works

1. Convert the input to greyscale.
2. Use `ImageOps.pad` with black fill to reach dimensions divisible by 10.
   This follows the notebook and can slightly resize the image.
3. Read 10×10 tiles from left to right and top to bottom. Normalize their pixels
   by 255 and flatten each tile into 100 features.
4. Use the saved `SGDClassifier` to predict one of 94 character filenames.
5. Paste the matching original PNG tiles into the output image.

The converter uses the supplied character PNGs directly. It does not regenerate
characters or substitute fonts. Prediction runs one row at a time to reduce memory
use. The output is a PNG of ASCII characters, not editable text.

## Training and development notebook

The notebook contains the original experiments: character generation, a random
forest baseline, preparation of edge-filtered training tiles, nearest-character
label assignment, incremental SGD training, evaluation, and image reconstruction.
The saved SGD model uses logistic loss and L2 regularization with alpha `1e-5`.

To work with the notebook:

```bash
python -m pip install -r requirements-notebook.txt
python -m jupyterlab
```

Open `notebooks/model_training_and_development.ipynb`. Change the paths in the
first code cell and supply your own images in the documented `data/` folders.
The optional download cell references the
[Image Dataset for Unsupervised Clustering](https://www.kaggle.com/datasets/heavensky/image-dataset-for-unsupervised-clustering).
It does not automatically copy downloaded images into the experiment folders.
Training data and generated intermediates are not included.

Character generation is disabled by default because both sets of PNGs are
included. To deliberately regenerate them, configure `FONT_PATH` and set
`REGENERATE_CHARACTERS = True`. The original font was Segoe UI. Regeneration
replaces the supplied PNGs and can change their appearance.

The notebook has generic paths, revised comments, and cleared outputs. Small
portability fixes include compatible string quoting, dynamic file counts, and
saving the final partial feature chunk. Training on a large dataset can create
many tile files and feature arrays. Running the SGD export cell replaces the model
at the configured path.

## Limitations and reproducibility

- Training uses edge-filtered tiles; final inference uses greyscale without edge
  filtering. The original inference behaviour is preserved.
- Training labels come from nearest-character comparisons. Label accuracy is
  not a measure of visual quality.
- The original SGD split is by feature chunk. Tiles from one source image may
  appear in both training and testing sets.
- The early random forest experiment uses uint8 distance arithmetic, which can
  overflow. The later SGD labeling uses normalized floating-point arrays.
- Scikit-learn is pinned to 1.8.0 to match the saved model. Load only trusted
  joblib files. The Flask server is intended for local demonstration.

No project license has been assigned in this package.
