import io
import os
import flask
import json
from flask import Flask
from google.cloud import vision
from google.cloud.vision import types
from flask import jsonify
from flask_cors import CORS
from random import choice
from string import ascii_lowercase
import base64
import PIL
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "./uploads"
CORS(app)
client = vision.ImageAnnotatorClient()



def process_image(image, city):
    a = image.size[0] / 9
    b = image.size[1] / 16
    
    c = min(a, b)
    
    a = (image.size[0] - c * 9) // 2
    b = (image.size[1] - c * 16) // 2
    
    image = image.crop((a, b, a + c * 9, b + c * 16))
    image = image.resize((540, 960))
    
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("Graphik-Black-Web.ttf", 30)
    draw.text((145, 142),"Мое #МегаПутешествие", fill=(0,185,86,255),font=font)
    
    
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("Graphik-Black-Web.ttf", 70)
    draw.text((250, 60), city, fill=(115,25,130,255),font=font)
    
    return image


def get_random_filename():
    return "".join([choice(ascii_lowercase) for i in range(15)]) + ".jpg"


@app.route("/process_photo", methods=['POST'])
def process_photo():
    print("starting processing")
    file = flask.request.files.get('photo', None)

    if file is not None:
        photo_content = file.read()
    else:
        data = json.loads(flask.request.data.decode())
        city = data["trip"]
        photo_content = base64.decodebytes(data["b64photo"].encode('utf-8'))


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
        fpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # with open(fpath, "wb") as f:
        #     f.write(photo_content)

        # image = PIL.Image.open(fpath)
        image = Image.open(io.BytesIO(photo_content))
        image = process_image(image, city)
        image.save(fpath)

        response["filename"] = filename

    print("done")
    return jsonify(response)

    

@app.route('/img/<path:filename>') 
def send_file(filename): 
    return flask.send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == "__main__":
    app.run()