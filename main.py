from flask import *
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage, JoinEvent, FlexSendMessage, ImageSendMessage
import os
import re

from file_mng import *
from okayu import *
from sec import *
from sinulist import *
from baseball import gen_score_json

app = Flask(__name__)

pic_save_availavle = False
kaitamono = ""
memo = ""
sinulist = []
kaitalist = {}
okayu = {}

def loadfiles():
    global sinulist, kaitalist, okayu, memo
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

def set_memo(text):
    global memo
    memo = text
    make_pkl(memo, "memo")

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

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
@app.route('/.well-known/acme-challenge/<filename>')
def well_known(filename):
    return render_template('.well-known/acme-challenge/'+ filename)

@app.route("/")
def hello():
    return "Sinulist Server Status: ONLINE"

@app.route("/img/<string:path>")
def send_image(path):
    dir = "img/"
    path = os.path.relpath(f"{os.getcwd()}/{dir}{path}")
    if os.path.commonprefix([dir, path]) == dir:
        if os.path.isfile(path):
            print("OK")
            return send_file(path)
        else: return "File not exists"
    else: return "Operation not allowed"

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
        messege_content = line_bot_api.get_message_content(message_id)
        pic_save(kaitalist, kaitamono, messege_content)
        pic_save_availavle = False
        text = f'{kaitamono}を保存しました!'
        line_bot_api.push_message(event.source.group_id, TextSendMessage(text))
        rmlist(sinulist, kaitamono)
        text = '死ぬまでには描くものリストから{0}を削除しました!'.format(kaitamono)
        line_bot_api.push_message(event.source.group_id, TextSendMessage(text))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    loadfiles()
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
            message_send = True
            #result += '死ぬまでには描くものリスト\n(クオリティは問わないものとする)\n{0}\n'.format(printlist())
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text='描くものリスト',
                    contents=gen_json(sinulist, "描くもの")
                )
            )
        elif (command == 'ドラゴンズ' or command == '中日'):
            oneshot = True
            message_send = True
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text='中日速報',
                    contents=gen_score_json("dragons")
                )
            )
        elif (command == 'エンゼルス' or command == 'エンジェルス'):
            oneshot = True
            message_send = True
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text='エンゼルス速報',
                    contents=gen_score_json("mlb_angels")
                )
            )
        elif (command == 'ドジャース' or command == 'ドジャーズ'):
            oneshot = True
            message_send = True
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text='ドジャース速報',
                    contents=gen_score_json("mlb_dodgers")
                )
            )
        elif command == 'メモ':
            if hastoken == True:
                set_memo(token)
                result += "メモに保存しました!\n"
            else:
                result += memo

        elif command == 'add' and hastoken == True:
            kakumono = token
            if checkls(sinulist, kakumono) == True:
                result += '{0}は既に存在しています!\n'.format(kakumono)
            else:
                result += '死ぬまでには描くものリストに{0}を追加しました!\n'.format(kakumono)
                status = '@hyorohyoro66 {0}'.format(token)
                addlist(sinulist, kakumono)
        elif command == 'remove' or command == 'delete' or command == 'rm' or command == "削除":
            if hastoken == True:
                try:
                    if token.isdecimal() == True:
                        tokennum = int(token)
                        kesumono = rmnum(sinulist, tokennum)
                        str = '死ぬまでには描くものリストから{0}を削除しました!\n'.format(kesumono)
                    else:
                        kesumono = token
                        str = '死ぬまでには描くものリストから{0}を削除しました!\n'.format(kesumono)
                        rmlist(sinulist, kesumono)
                except ValueError:
                    str = '{0}は存在しません!\n'.format(kesumono)
                result += str
            else:
                oneshot = True
                kesumono = rmrecent(sinulist)
                str = '死ぬまでには描くものリストから{0}を削除しました!\n'.format(kesumono)
                result += str
    #Picture Command
        elif (command == 'plist' or command == 'picls' or command == 'pshow' or command == "描いたもの") and hastoken==False:
            oneshot = True
            message_send = True
            '''
            tmp = []
            for n in kaitamono:
                tmp.append(kaitalist)
            '''
            #result += '描いたものリスト\n{0}\n'.format(pic_print())
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text='描くものリスト',
                    contents=gen_json(list(kaitalist.keys()), "描いたもの")
                )
            )
        elif (command == 'save' or command == 'comp' or command == 'complete' or command == '保存') and hastoken==True:
            #oneshot=True
            loadfiles()
            if checkls(sinulist, token) == False:
                result+='{0}は死ぬまでに描くものリストに存在しません!\n'.format(token)
            else:
                if pic_checkls(kaitalist, token) == True:
                    result+='{0}は既に存在しています!\n'.format(token)
                else:
                    pic_save_availavle = True
                    kaitamono = token
                    result += '{0}を保存します!\n画像を送信して下さい\n'.format(token)
        elif (command == 'pic' or command == 'showpic' or command == "見せて") and hastoken == True:
            oneshot = True
            haserror = False
            try:
                url = kaitalist[token]
            except KeyError:
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
            if pic_checkls(kaitalist, token) == True:
                pic_rmlist(kaitalist, token)
                result += '{0}の画像を削除しました!\n'.format(token)
            else:
                result += '{0}は存在しません!\n'.format(token)
        elif command == 'okayurm':
                #debug_pic1224()
                result += f"removed {okayu_del(okayu, token)}"

        elif command == "debug":
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
            okayu_up(okayu, profile.display_name, re.sub(r"\D", "", command))

        elif (command == "battle" and hastoken==True):
            oneshot = True
            profile = line_bot_api.get_profile(event.source.user_id)
            if token == 'everyone':
                result += okayu_showall(okayu, profile.display_name)
            else:
                if okayu_check(token) == False:
                    result += f'{token}は1d100草粥をプレイしていません!\n'
                else:
                    result += f'{profile.display_name}({okayu_num(okayu, profile.display_name)}草粥) VS {token}({okayu, okayu_num(token)}草粥)\n'
                    if(okayu_num(okayu, profile.display_name)>okayu_num(token)):
                        result += f'WINNER {profile.display_name}\n'
                    elif(okayu_num(okayu, profile.display_name)<okayu_num(token)):
                        result += f'WINNER {token}\n'
                    else:
                        result += 'DRAW\n'
        else:
            isNotCommand = True

    if isNotCommand == False and message_send == False:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(result.strip()))