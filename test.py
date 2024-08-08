from file_mng import Room

import os
import pickle

'''room = Room()
room.memo = "tesuto"
room.save2pkl()
'''

'''def loadfiles():
    global sinulist, kaitalist, okayu, memo, counter
    if os.path.exists('list.pkl'):
        with open('list.pkl','rb') as f:
            sinulist = pickle.load(f)
    if os.path.exists('kaita.pkl'):
        with open('kaita.pkl','rb') as f:
            kaitalist = pickle.load(f)
    if os.path.exists('okayu.pkl'):
        with open('okayu.pkl','rb') as f:
            okayu = pickle.load(f)
    if os.path.exists('memo.pkl'):
        with open('memo.pkl','rb') as f:
            memo = pickle.load(f)
    if os.path.exists('counter.pkl'):
        with open('counter.pkl','rb') as f:
            counter = pickle.load(f)

loadfiles()'''
room = Room()
if os.path.exists('RoomInfo.pkl'):
    with open('RoomInfo.pkl','rb') as f:
        room = pickle.load(f)

'''room.kakkoii = set()
room.save2pkl()'''

'''room.sinulist = sinulist
room.kaitalist = kaitalist
room.okayu = okayu
room.memo = memo
room.counter = counter'''

with open("kaita_urls", 'a') as f:
    for v in room.kaitalist.values():
        f.write(f"{v}\n")

