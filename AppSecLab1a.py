# Richard Yeung - ry821
# Sihao Chen - sc6094

from flask import Flask, render_template, request, send_file
from werkzeug import secure_filename
from spellchecker import SpellChecker
from io import BytesIO
from PIL import Image

app = Flask(__name__, static_folder='static')
ALLOWED_IMAGE_EXTENSIONS = set(["png, jpg, jpeg"])

IMAGE_ERROR_MSG = "There has been an error. Make sure you have correctly submitted an image file or a valid square size!"
TEXT_FILE_ERROR_MSG = "There has been an error. Make sure you have correctly submitted a text file!"


@app.route('/')
def home():
    return render_template('upload.html')

def is_image_file(filename):
    return filename.lower().endswith((".png", ".jpg", "jpeg"))

def is_text_file(filename):
    return filename.lower().endswith(".txt")

@app.route("/resize", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "imageFile" not in request.files:
            return IMAGE_ERROR_MSG
        f = request.files["imageFile"]

        if f and is_image_file(f.filename):
            size = int(request.form["resizeValue"])

            if size <= 0 or size >= 10000:
                return IMAGE_ERROR_MSG

            img = Image.open(f)
            img = img.resize((size, size), Image.ANTIALIAS)

            img_io = BytesIO()
            img.save(img_io, "jpeg")
            img_io.seek(0)
            return send_file(img_io,
                             attachment_filename="resized_image.jpg",
                             as_attachment=True,
                             mimetype="image/jpg")
    return IMAGE_ERROR_MSG

@app.route("/spellchecker", methods=["GET", "POST"])
def spellchecker():
    if request.method == 'POST':
        if "file" not in request.files:
            return TEXT_FILE_ERROR_MSG
        f = request.files['file']

        if f and is_text_file(f.filename):
            f.save(secure_filename(f.filename))
            spell = SpellChecker()
            checkfile = open(f.filename, 'r')
            
            spellcheckfile = BytesIO()
            for line in checkfile:
                for word in line.split():
                    spellcheckfile.write(spell.correction(word).encode())

                    spellcheckfile.write(b' ')

                spellcheckfile.write(b'\n')
            spellcheckfile.seek(0)

            return send_file(spellcheckfile, attachment_filename='spellchecked.txt', as_attachment=True,
                             mimetype='text/csv')
    return TEXT_FILE_ERROR_MSG


app.secret_key = 'some key that you will never guess'
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)
