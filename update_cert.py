from flask import *

app = Flask(__name__)

@app.route('/')
def index():
    return "This is HTTP Server"

@app.route('/.well-known/acme-challenge/<filename>')
def well_known(filename):
    return render_template('.well-known/acme-challenge/'+ filename)

app.run(host = "0.0.0.0", port = 80)