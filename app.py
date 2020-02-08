import io
import os
import flask
from flask import Flask
from google.cloud import vision
from google.cloud.vision import types
from flask import jsonify
from flask_cors import CORS
from random import choice
from string import ascii_lowercase


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "./uploads"
CORS(app)
client = vision.ImageAnnotatorClient()


def get_random_filename():
    return "".join([choice(ascii_lowercase) for i in range(15)]) + ".jpg"


@app.route("/process_photo", methods=['POST'])
def process_photo():
    file = flask.request.files.get('photo', '')
    photo_content = file.read()


    photo = types.Image(content=photo_content)
    landmark_response = client.landmark_detection(image=photo)
    labels_response = client.label_detection(image=photo)


    response = {"landmarks": "", "is_selfie": False, "filename":""}


    if landmark_response:
        response["landmarks"] = [i.description for i in landmark_response.landmark_annotations]

        for label in labels_response.label_annotations:
            if label.description in ["Selfie", "Tourism"]:
                response["is_selfie"] = True

        filename = get_random_filename()
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "wb") as f:
            f.write(photo_content)
        response["filename"] = filename

    return jsonify(response)


@app.route('/img/<path:filename>') 
def send_file(filename): 
    return flask.send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == "__main__":
    app.run()