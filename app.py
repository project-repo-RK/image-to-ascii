# Run the local webpage and pass uploaded images to the converter.
from io import BytesIO

from flask import Flask, jsonify, render_template, request, send_file
from PIL import Image, UnidentifiedImageError

from converter import image_to_ascii

app = Flask(__name__)

# Allow high-resolution images while keeping local memory use reasonable.
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
max_pixels = 24_000_000


# Show the upload page when the user opens the local address.
@app.get('/')
def index():
    return render_template('index.html')


# Return a readable message if the uploaded file exceeds the size limit.
@app.errorhandler(413)
def too_large(error):
    return jsonify(error='Choose an image smaller than 32 MB.'), 413


# Convert the uploaded image and return the result as a PNG.
@app.post('/convert')
def convert():
    upload = request.files.get('image')
    if upload is None or not upload.filename:
        return jsonify(error='Choose an image first.'), 400

    try:
        with Image.open(upload.stream) as img:
            # Check the file before loading all of its pixels into memory.
            if img.format not in {'PNG', 'JPEG', 'WEBP', 'BMP'}:
                return jsonify(error='Use a PNG, JPEG, WebP, or BMP image.'), 400
            if img.width * img.height > max_pixels:
                return jsonify(error='Choose an image with at most 24 million pixels.'), 400

            img.load()
            output = image_to_ascii(img)
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        return jsonify(error='This image could not be read. Choose a valid image file.'), 400

    # Keep the result in memory instead of saving uploaded images to disk.
    image_file = BytesIO()
    output.save(image_file, 'PNG')
    image_file.seek(0)
    return send_file(image_file, mimetype='image/png', download_name='ascii-output.png', max_age=0)


# Listen on this computer only. Stop the server with Ctrl+C.
if __name__ == '__main__':
    print('Open http://127.0.0.1:5000 in your browser.')
    app.run(host='127.0.0.1', port=5000, debug=False)
