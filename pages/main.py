from flask import Flask, send_file
import os
import pickle
import sys
sys.path.append('/root/py/kakumono/tools')
from file_mng import Room

app = Flask(__name__)

def load_room():
    if os.path.exists('../pkl/RoomInfo.pkl'):
        with open('../pkl/RoomInfo.pkl','rb') as f:
            room = pickle.load(f)
    return room

def commandsplit(line):
    commandlist = line.splitlines()
    return commandlist

def linesplit(commandlist):
    pc = commandlist.split()
    command = pc[0]
    token = ''
    for n in range(len(pc)):
        if n == 0:
            pass
        elif n != len(pc) - 1:
            token += '{0} '.format(pc[n])
        else:
            token += '{0}'.format(pc[n])
    line = {'command':command,'token':token}
    return line

@app.route("/")
def hello():
    return "ok"

@app.route("/kawaii")
def send_kawaii_html():
    room = load_room()
    return room.gen_onnna_json()
    
@app.route("/kakkoii")
def send_kakkoii_html():
    room = load_room()
    return room.gen_kakkoii_json()

@app.route("/tuyosou")
def send_tuyosou_html():
    room = load_room()
    return room.gen_tuyosou_json()

@app.route("/yowasou")
def send_yowasou_html():
    room = load_room()
    return room.gen_yowasou_json()

@app.route("/img/<string:path>")
def send_image(path):
    dir = "../tools/img/"
    path = os.path.relpath(f"{os.getcwd()}/{dir}{path}")
    if os.path.commonprefix([dir, path]) == dir:
        if os.path.isfile(path):
            print("OK")
            return send_file(path)
        else: return "File not exists"
    else: return "Operation not allowed"
