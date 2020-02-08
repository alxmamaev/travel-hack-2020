import io
import os
import flask
from flask import Flask
from google.cloud import vision
from google.cloud.vision import types
from flask import jsonify


app = Flask(__name__)
client = vision.ImageAnnotatorClient()


@app.route("/process_photo", methods=['POST'])
def process_photo():
    photo_content = flask.request.files.get('photo', '').read()


    photo = types.Image(content=photo_content)
    landmark_response = client.landmark_detection(image=photo)
    labels_response = client.label_detection(image=photo)


    response = {"landmarks": "", "is_selfie": False}


    if landmark_response:
        response["landmarks"] = [i.description for i in landmark_response.landmark_annotations]

        for label in labels_response.label_annotations:
            if label.description in ["Selfie", "Tourism"]:
                response["is_selfie"] = True
    
    return jsonify(response)


if __name__ == "__main__":
    app.run()