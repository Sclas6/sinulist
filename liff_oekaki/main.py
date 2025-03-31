from flask import Flask, request, render_template, make_response, send_file
from flask_bootstrap import Bootstrap
import os
import uuid
import base64
from PIL import Image
import traceback
import logger

app = Flask(__name__, static_folder='imgs')
bootstrap = Bootstrap(app)

@app.route('/')
def do_get():
    return render_template('index.html')

@app.route('/saveimage', methods=['POST'])
def saveimage():
    try:
        event = request.form.to_dict()

        dir_name = 'imgs'

        img_name = uuid.uuid4().hex

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        with open(os.path.join(dir_name, '{}.jpg'.format(img_name)), 'wb') as img:
            img.write(base64.b64decode(event['image'].split(",")[1]))
        original = Image.open(os.path.join(dir_name, '{}.jpg'.format(img_name)))
        
        if(original.format != 'JPEG'):
            return make_response('Unsupported image type.', 400)

        original.thumbnail((240, 240), Image.LANCZOS)

        original.save(os.path.join(dir_name, '{}_240.jpg'.format(img_name)), 'JPEG')
    except:
        logger.error(traceback.format_exc())
    return make_response(img_name, 200)

@app.route("/imgs/<string:path>")
def send_image(path):
    dir = "imgs/"
    path = os.path.relpath(f"{os.getcwd()}/{dir}{path}")
    if os.path.commonprefix([dir, path]) == dir:
        if os.path.isfile(path):
            print("OK")
            return send_file(path)
        else: return "File not exists"
    else: return "Operation not allowed"
