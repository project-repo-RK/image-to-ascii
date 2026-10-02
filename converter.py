# Load the trained model and use it to turn image tiles into ASCII characters.
import argparse
import os

import numpy as np
from joblib import load
from PIL import Image, ImageOps

# Keep the model and character paths relative to this file.
project_folder = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(project_folder, 'models', 'sgd_ascii_model.joblib')
chars_path = os.path.join(project_folder, 'assets', 'ascii_images_shrunk')
tile_size = 10

model = load(model_path)

# Load the supplied 10x10 character images once, ready for each conversion.
char_cache = {}
for filename in os.listdir(chars_path):
    if filename.endswith('.png'):
        path = os.path.join(chars_path, filename)
        with Image.open(path) as img:
            char_cache[filename] = img.copy()


def image_modifier(img, size):
    # Convert to greyscale so each tile contains 100 pixel values.
    greyscale = img.convert('L')

    # Find the extra width and height needed for complete tiles.
    x = 0
    y = 0
    if greyscale.width % size != 0:
        x = size - greyscale.width % size
    if greyscale.height % size != 0:
        y = size - greyscale.height % size

    # Use the same black padding as the final notebook function.
    # ImageOps.pad can also resize slightly to fit the new dimensions.
    new_size = (greyscale.width + x, greyscale.height + y)
    return ImageOps.pad(greyscale, new_size, color='#000')


def image_to_ascii(img):
    # Prepare the image and make a blank canvas for the converted tiles.
    img = image_modifier(img, tile_size)
    width, height = img.size
    output = Image.new('L', (width, height), color=255)

    # Work through the image from top to bottom, one row of tiles at a time.
    # Predicting each row separately keeps memory use low for larger images.
    for top in range(0, height, tile_size):
        batch_img = []
        for left in range(0, width, tile_size):
            crop_area = (left, top, left + tile_size, top + tile_size)
            cropped_img = img.crop(crop_area)

            # Normalize the pixels to 0-1 and flatten the tile for the model.
            img_arr = np.asarray(cropped_img, dtype=np.float32) / 255.0
            batch_img.append(img_arr.flatten())

        # Predict a character filename for each tile in this row.
        batch_arr = np.array(batch_img)
        batch_pred = model.predict(batch_arr)

        # Paste the original character images into their matching positions.
        left = 0
        for prediction in batch_pred:
            char_img = char_cache[prediction]
            output.paste(char_img, (left, top))
            left = left + tile_size

    return output


# Allow this file to run on its own: python converter.py input.jpg output.png
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert an image into an ASCII PNG.')
    parser.add_argument('input')
    parser.add_argument('output')
    args = parser.parse_args()

    with Image.open(args.input) as img:
        output = image_to_ascii(img)
        output.save(args.output, 'PNG')
    print(f'Saved {args.output}')
