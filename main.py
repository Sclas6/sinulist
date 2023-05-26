from flask import *
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, JoinEvent
from linebot.models.messages import ImageMessage
from linebot.models.send_messages import ImageSendMessage
import os
import re
import ssl
import dropbox
import pickle
import json

app = Flask(__name__)

pic_save_availavle = False
kaitamono = ''
sinulist = []
kaitalist = {}
okayu = {}
sec = {}
with open("secrets.json") as f:
    sec = json.load(f)

ACCESS_TOKEN = sec["dropbox_token"]
LINE_ACCESS_TOKEN = sec["line_acc_token"]
LINE_CHANNEL_SECRET = sec["line_acc_sec"]
'''
T_API_KEY = sec["twitter_api_key"]
T_API_SEC = sec["twitter_api_sec"]
T_ACC_TOKEN = sec["twitter_acc_token"]
T_ACC_SEC = sec["twitter_acc_sec"]
tweetId='1335593079059873795'
'''

def debug_pic1224():
    pass

def checkls(kakumono):
    global sinulist
    juuhuku=False
    for n in range(len(sinulist)):
        if kakumono == sinulist[n]:
            juuhuku = True
    if juuhuku == True:
        return True
    else:
        return False

def addlist(kakumono):
    global sinulist
    sinulist.append(kakumono)
    with open('list.pkl','wb') as f:
        pickle.dump(sinulist,f)

def loadfiles():
    global sinulist, kaitalist, okayu
    if os.path.exists('list.pkl'):
        with open('list.pkl','rb') as f:
            sinulist = pickle.load(f)
    if os.path.exists('kaita.pkl'):
        with open('kaita.pkl','rb') as f:
            kaitalist = pickle.load(f)
    if os.path.exists('okayu.pkl'):
        with open('okayu.pkl','rb') as f:
            okayu = pickle.load(f)

def pic_checkls(content):
    global kaitalist
    for n in kaitalist:
        if content == n:
            return True
    return False

def pic_save(kaitamono,content):
    client = dropbox.Dropbox(ACCESS_TOKEN)
    global kaitalist
    with open(f'{kaitamono}.jpg','wb') as f:
        for chunk in content.iter_content():
            f.write(chunk)
    #upload
    with open(f'{kaitamono}.jpg','rb') as f:
        client.files_upload(f.read(),f'/{kaitamono}.jpg',mode=dropbox.files.WriteMode.overwrite)
    #del
    os.remove(f'{kaitamono}.jpg')
    #create link
    setting = dropbox.sharing.SharedLinkSettings(requested_visibility=dropbox.sharing.RequestedVisibility.public)
    link = client.sharing_create_shared_link_with_settings(path=f'/{kaitamono}.jpg', settings=setting)
    #get link
    links = client.sharing_list_shared_links(path=f'/{kaitamono}.jpg',direct_only=True).links
    if links is not None:
        for link in links:
            url = link.url
            url = url.replace('www.dropbox','dl.dropboxusercontent').replace('?dl=0','')
    kaitalist[kaitamono] = url
    with open('kaita.pkl','wb') as f:
        pickle.dump(kaitalist,f)

def pic_print():
    global kaitalist
    with open('kaita.pkl','rb') as f:
        kaitalist = pickle.load(f)
    string = ''
    tmp = True
    for n in kaitalist:
        if tmp == True:
            string += '  ･{0}'.format(n)
            tmp = False
        else:
            string += '\n  ･{0}'.format(n)
    return string

def pic_showpic(content):
    global kaitalist
    if os.path.exists('kaita.pkl'):
        with open('kaita.pkl','rb') as f:
            kaitalist = pickle.load(f)
    return kaitalist[content]

def pic_rmlist(kesumono):
    global kaitalist
    kaitalist.pop(kesumono)
    with open('kaita.pkl','wb') as f:
        pickle.dump(kaitalist,f)

def printlist():
    global sinulist
    with open('list.pkl','rb') as f:
        sinulist = pickle.load(f)
    string = ''
    for n in range(len(sinulist)):
        if n == 0:
            string += '  ･{0}'.format(sinulist[n])
        else:
            string += '\n  ･{0}'.format(sinulist[n])
    return string

def rmlist(kakumono):
    global sinulist
    sinulist.remove(kakumono)
    with open('list.pkl','wb') as f:
        pickle.dump(sinulist,f)

def rmrecent():
    global sinulist
    str = sinulist[-1]
    rmlist(sinulist[-1])
    return str

def rmnum(num):
    global sinulist
    str = sinulist[num-1]
    rmlist(sinulist[num-1])
    return str

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

def okayu_up(key,value):
    global okayu
    okayu[key] = int(value)
    with open('okayu.pkl','wb') as f:
        pickle.dump(okayu,f)

def okayu_num(key):
    global okayu
    return int(okayu[key])

def okayu_check(key):
    global okayu
    return key in okayu.keys()

def okayu_diff(key1,key2):
    global okayu
    result = ''
    if(okayu_num(key1)>okayu_num(key2)):
        result += f"WINNER {key1}"
    elif(okayu_num(key1)<okayu_num(key2)):
        result += f"WINNER {key2}"
    else:
        result += "DRAW"
    return result

def okayu_showall(key):
    global okayu
    yourscore = okayu_num(key)
    result = f"{key}({yourscore}草粥)VS\n"
    for k in okayu:
        if(key == k):
            continue
        result += f'    {k}({okayu_num(k)}草粥)\n        {okayu_diff(key,k)}\n'
    return result

def okayu_del(key):
    global okayu
    if okayu_check(key) == True:
        val = okayu.pop(key)
        with open('okayu.pkl','wb') as f:
            pickle.dump(okayu,f)
        return val

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
@app.route('/.well-known/acme-challenge/<filename>')
def well_known(filename):
    return render_template('.well-known/acme-challenge/'+ filename)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(JoinEvent)
def join_event(event):
    str_join = 'I am @hyorohyoro66 !!!!!!!'
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(str_join))

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    global pic_save_availavle
    global kaitamono
    text = ''
    if pic_save_availavle == True:
        message_id = event.message.id
        messege_content=line_bot_api.get_message_content(message_id)
        pic_save(kaitamono, messege_content)
        pic_save_availavle = False
        text = f'{kaitamono}を保存しました!'
        line_bot_api.push_message(event.source.group_id,TextSendMessage(text))
        rmlist(kaitamono)
        text = '死ぬまでには描くものリストから{0}を削除しました!'.format(kaitamono)
        line_bot_api.push_message(event.source.group_id,TextSendMessage(text))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    result = ''
    oneshot = False
    message_send = False
    global pic_save_availavle
    global kaitamono
    linelist = commandsplit(event.message.text)
    while len(linelist) != 0 and oneshot == False:
        line = linelist.pop(0)
        comset = linesplit(line)
        command = comset['command']
        token = comset['token']
        hastoken = False if token == '' else True
        isNotCommand = False

        #groupid=line_bot_api.get_profile(event.source.group_id)

        if (command == 'show' or command == '描くもの'):
            oneshot = True
            result += '死ぬまでには描くものリスト\n(クオリティは問わないものとする)\n{0}\n'.format(printlist())

        elif command == 'add' and hastoken == True:
            kakumono = token
            if checkls(kakumono) == True:
                result += '{0}は既に存在しています!\n'.format(kakumono)
            else:
                result += '死ぬまでには描くものリストに{0}を追加しました!\n'.format(kakumono)
                status = '@hyorohyoro66 {0}'.format(token)
                addlist(kakumono)
        elif command == 'remove' or command == 'delete' or command == 'rm' or command == "削除":
            if hastoken == True:
                try:
                    if token.isdecimal() == True:
                        tokennum = int(token)
                        kesumono = rmnum(tokennum)
                        str = '死ぬまでには描くものリストから{0}を削除しました!\n'.format(kesumono)
                    else:
                        kesumono = token
                        str = '死ぬまでには描くものリストから{0}を削除しました!\n'.format(kesumono)
                        rmlist(kesumono)
                except ValueError as error:
                    str = '{0}は存在しません!\n'.format(kesumono)
                result += str
            else:
                oneshot = True
                kesumono = rmrecent()
                str = '死ぬまでには描くものリストから{0}を削除しました!\n'.format(kesumono)
                result += str
    #Picture Command
        elif (command == 'plist' or command == 'picls' or command == 'pshow' or command == "描いたもの") and hastoken==False:
            oneshot = True
            result += '描いたものリスト\n{0}\n'.format(pic_print())
        elif (command == 'save' or command == 'comp' or command == 'complete' or command == '保存') and hastoken==True:
            #oneshot=True
            loadfiles()
            if checkls(token) == False:
                result+='{0}は死ぬまでに描くものリストに存在しません!\n'.format(token)
            else:
                if pic_checkls(token) == True:
                    result+='{0}は既に存在しています!\n'.format(token)
                else:
                    pic_save_availavle = True
                    kaitamono = token
                    result += '{0}を保存します!\n画像を送信して下さい\n'.format(token)
        elif (command == 'pic' or command == 'showpic' or command == "見せて") and hastoken == True:
            oneshot = True
            haserror = False
            try:
                url = pic_showpic(token)
            except KeyError as error:
                result += '{0}は存在しません!\n'.format(token)
                haserror = True
            if haserror != True:
                message_send = True
                line_bot_api.reply_message(
                    event.reply_token,
                    ImageSendMessage(
                        preview_image_url=url,
                        original_content_url=url
                    )
                )
        elif (command == 'prm' or command == 'pdelete' or command == '画像削除' or command == 'picrm')and hastoken == True:
            if pic_checkls(token) == True:
                pic_rmlist(token)
                result += '{0}の画像を削除しました!\n'.format(token)
            else:
                result += '{0}は存在しません!\n'.format(token)
        elif command == 'okayurm':
                #debug_pic1224()
                result += f"removed {okayu_del(token)}"

        elif command == "debug":
            debug_pic1224()
            result += "debug"

        elif command == '名取さなしりとり':
            message_send = True
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage('名取さな'))

        elif command == 'test':
            kakumono=token
            '''
            payload={'value1':'@hyorohyoro66 \n{0}'.format(token)}
            requests.post(WEB_HOOK_URL,data=payload)
            '''
            message_send = True
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(event.source.group_id))

        elif( command == "okayu" or command == "おかゆ") and (hastoken == False):
            result += "https://shindanmaker.com/957861"
            oneshot = True

        elif (re.match('[0-9]{1,3}草粥',command)):
            message_send = True
            oneshot = True
            profile = line_bot_api.get_profile(event.source.user_id)
            okayu_up(profile.display_name,re.sub(r"\D", "", command))

        elif (command == "battle" and hastoken==True):
            oneshot = True
            profile = line_bot_api.get_profile(event.source.user_id)
            if token == 'everyone':
                result += okayu_showall(profile.display_name)
            else:
                if okayu_check(token) == False:
                    result += f'{token}は1d100草粥をプレイしていません!\n'
                else:
                    result += f'{profile.display_name}({okayu_num(profile.display_name)}草粥) VS {token}({okayu_num(token)}草粥)\n'
                    if(okayu_num(profile.display_name)>okayu_num(token)):
                        result += f'WINNER {profile.display_name}\n'
                    elif(okayu_num(profile.display_name)<okayu_num(token)):
                        result += f'WINNER {token}\n'
                    else:
                        result += 'DRAW\n'
        else:
            isNotCommand = True

    if isNotCommand == False and message_send == False:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(result.strip()))