from fastapi import FastAPI, Request, Header, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, ImageMessage, StickerMessage, TextSendMessage, JoinEvent, FlexSendMessage, ImageSendMessage
from linebot.v3.messaging import TextMessage
import json
import os
import re
import random

import sys
sys.path.append('/root/py/kakumono/tools')
from file_mng import *
from okayu import *
from sec import *
from sinulist import *
from baseball import gen_score_json
from uno_game import *
from uno_json import *
from yugioh import get_card_img, get_card_img_2, get_card_img_poke

def reply_message_v2(self, reply_token, messages, notification_disabled=False, timeout=None):
    if not isinstance(messages, (list, tuple)):
        messages = [messages]
    data = {
        'replyToken': reply_token,
        'messages': [message for message in messages],
        'notificationDisabled': notification_disabled,
    }
    self._post(
        '/v2/bot/message/reply', data=json.dumps(data), timeout=timeout
    )

LineBotApi.reply_message_v2 = reply_message_v2
app = FastAPI()
origins = [
    "http://localhost:3000",
    "https://sclas.xyz:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
templates = Jinja2Templates(directory="templates")

def load_room() -> Room:
    if os.path.exists('../pkl/RoomInfo.pkl'):
        with open('../pkl/RoomInfo.pkl','rb') as f:
            room = pickle.load(f)
    return room

def load_uno(id):
    if os.path.exists(f'../pkl/uno/{id}_uno.pkl'):
        with open(f'../pkl/uno/{id}_uno.pkl','rb') as f:
            game = pickle.load(f)
            return game
    return None

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

@app.get('/.well-known/acme-challenge/{filename}')
def well_known(request: Request, filename):
    return templates.TemplateResponse(
        request=request, name=f".well-known/acme-challenge/{filename}"
    )

@app.get("/deck/kawaii")
def send_kawaii_html():
    room = load_room()
    return room.gen_onnna_api()
    
@app.get("/deck/kakkoii")
def send_kakkoii_html():
    room = load_room()
    return room.gen_kakkoii_api()

@app.get("/deck/tuyosou")
def send_tuyosou_html():
    room = load_room()
    return room.gen_tuyosou_api()

@app.get("/deck/yowasou")
def send_yowasou_html():
    room = load_room()
    return room.gen_yowasou_api()

@app.get("/")
def hello():
    return "Sinulist Server Status: ONLINE"

@app.post("/callback")
async def callback(
    request: Request,
    background_tasks: BackgroundTasks,
    x_line_signature=Header(None),
    summary="CallBack from LINE Message API"
):
    body = await request.body()
    #app.logger.info("Request body: " + body)
    try:
        background_tasks.add_task(
            handler.handle, body.decode("utf-8"), x_line_signature
        )
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return 'OK'

@handler.add(JoinEvent)
def join_event(event):
    str_join = 'I am @hyorohyoro66 !!!!!!!'
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=str_join))

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    room = load_room()
    text = ''
    if room.pic_save_availavle == True:
        message_id = event.message.id
        messege_content = line_bot_api.get_message_content(message_id)
        pic_save(room.kaitalist, room.kaitamono, messege_content)
        room.pic_save_availavle = False
        text = f'{room.kaitamono}を保存しました!'
        line_bot_api.push_message(event.source.group_id, TextSendMessage(text=text))
        rmlist(room.sinulist, room.kaitamono)
        text = '死ぬまでには描くものリストから{0}を削除しました!'.format(room.kaitamono)
        line_bot_api.push_message(event.source.group_id, TextSendMessage(text=text))
        room.save2pkl()

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker(event):
    room = load_room()
    sticker_id = event.message.sticker_id
    if sticker_id == "9267865":
        profile = line_bot_api.get_profile(event.source.user_id)
        card_url, _ = room.drow(profile.display_name)
        room.save2pkl()
        line_bot_api.reply_message(event.reply_token,
            ImageSendMessage(
                preview_image_url=card_url,
                original_content_url=card_url
            )
        )

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    room = load_room()
    result = ''
    oneshot = False
    message_send = False
    linelist = commandsplit(event.message.text)

    try:
        game = load_uno(event.source.group_id)
    except: pass
    try:
        while len(linelist) != 0 and oneshot == False:
            line = linelist.pop(0)
            comset = linesplit(line)
            command = comset['command']
            token = comset['token']
            hastoken = False if token == '' else True
            #groupid=line_bot_api.get_profile(event.source.group_id)

            print(command)

            if (command == 'show' or command == '描くもの'):
                oneshot = True
                message_send = True
                #result += '死ぬまでには描くものリスト\n(クオリティは問わないものとする)\n{0}\n'.format(printlist())
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text='描くものリスト',
                        contents=gen_json(list(room.sinulist.keys()), "描くもの")
                    )
                )
            elif (command == 'ドラゴンズ' or command == '中日'):
                oneshot = True
                message_send = True
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text='中日速報',
                        contents=gen_score_json("dragons", "../tools/")
                    )
                )
            elif (command == 'タイガース' or command == '阪神'):
                oneshot = True
                message_send = True
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text='阪神速報',
                        contents=gen_score_json("tigers", "../tools/")
                    )
                )
            elif (command == 'カープ' or command == '広島'):
                oneshot = True
                message_send = True
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text='広島速報',
                        contents=gen_score_json("carp", "../tools/")
                    )
                )
            elif (command == 'ベイスターズ' or command == 'DeNA'):
                oneshot = True
                message_send = True
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text='横浜速報',
                        contents=gen_score_json("baystars", "../tools/")
                    )
                )
            elif (command == 'ジャイアンツ' or command == '巨人'):
                oneshot = True
                message_send = True
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text='巨人速報',
                        contents=gen_score_json("giants", "../tools/")
                    )
                )
            elif (command == 'ヤクルト'):
                oneshot = True
                message_send = True
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text='ヤクルト速報',
                        contents=gen_score_json("swallows", "../tools/")
                    )
                )
            elif (command == 'ソフトバンク'):
                oneshot = True
                message_send = True
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text='ソフトバンク速報',
                        contents=gen_score_json("hawks", "../tools/")
                    )
                )
            elif (command == 'バッファローズ' or command == 'オリックス'):
                oneshot = True
                message_send = True
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text='オリックス速報',
                        contents=gen_score_json("buffaloes", "../tools/")
                    )
                )
            elif (command == 'ロッテ' or command == '千葉'):
                oneshot = True
                message_send = True
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text='ロッテ速報',
                        contents=gen_score_json("marines", "../tools/")
                    )
                )
            elif (command == 'イーグルス' or command == '楽天'):
                oneshot = True
                message_send = True
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text='楽天速報',
                        contents=gen_score_json("eagles", "../tools/")
                    )
                )
            elif (command == 'ライオンズ' or command == '西武'):
                oneshot = True
                message_send = True
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text='西武速報',
                        contents=gen_score_json("lions", "../tools/")
                    )
                )
            elif (command == '日ハム' or command == 'ハム'):
                oneshot = True
                message_send = True
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text='日ハム速報',
                        contents=gen_score_json("fighters", "../tools/")
                    )
                )
            elif (command == 'エンゼルス' or command == 'エンジェルス'):
                oneshot = True
                message_send = True
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text='エンゼルス速報',
                        contents=gen_score_json("mlb_angels", "../tools/")
                    )
                )
            elif (command == 'ドジャース' or command == 'ドジャーズ'):
                oneshot = True
                message_send = True
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text='ドジャース速報',
                        contents=gen_score_json("mlb_dodgers", "../tools/")
                    )
                )
            elif (command == 'Wソックス' or command == 'ホワイトソックス'):
                oneshot = True
                message_send = True
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text='Wソックス速報',
                        contents=gen_score_json("mlb_whitesox", "../tools/")
                    )
                )
            elif command == 'メモ':
                if hastoken == True:
                    room.memo = token
                    result += "メモに保存しました!\n"
                else:
                    result += room.memo
            elif command == "when" and hastoken == True:
                if checkls(room.sinulist, token) == True:
                    result += f"{token}の追加日時は{room.sinulist[token].strftime('%Y年%m月%d日 %H時%M分')}です!"
                else: result += '{0}は存在しません!\n'.format(token)
            elif command == 'add' and hastoken == True:
                kakumono = token
                if checkls(room.sinulist, kakumono) == True:
                    result += '{0}は既に存在しています!\n'.format(kakumono)
                else:
                    result += '死ぬまでには描くものリストに{0}を追加しました!\n'.format(kakumono)
                    status = '@hyorohyoro66 {0}'.format(token)
                    addlist(room.sinulist, kakumono)
            elif command == 'remove' or command == 'delete' or command == 'rm' or command == "削除":
                if hastoken == True:
                    try:
                        kesumono = token
                        str = '死ぬまでには描くものリストから{0}を削除しました!\n'.format(kesumono)
                        rmlist(room.sinulist, kesumono)
                    except ValueError:
                        str = '{0}は存在しません!\n'.format(kesumono)
                    result += str
                else:
                    oneshot = True
                    kesumono = rmrecent(room.sinulist)
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
                        contents=gen_json(list(room.kaitalist.keys()), "描いたもの")
                    )
                )
            elif (command == 'save' or command == 'comp' or command == 'complete' or command == '保存') and hastoken==True:
                #oneshot=True
                if checkls(room.sinulist, token) == False:
                    result+='{0}は死ぬまでに描くものリストに存在しません!\n'.format(token)
                else:
                    if pic_checkls(room.kaitalist, token) == True:
                        result+='{0}は既に存在しています!\n'.format(token)
                    else:
                        room.pic_save_availavle = True
                        room.kaitamono = token
                        result += '{0}を保存します!\n画像を送信して下さい\n'.format(token)
            elif (command == 'pic' or command == 'showpic' or command == "見せて") and hastoken == True:
                oneshot = True
                haserror = False
                try:
                    url = room.kaitalist[token]
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
                if pic_checkls(room.kaitalist, token) == True:
                    pic_rmlist(room.kaitalist, token)
                    result += '{0}の画像を削除しました!\n'.format(token)
                else:
                    result += '{0}は存在しません!\n'.format(token)
            elif command == 'okayurm':
                    #debug_pic1224()
                    result += f"removed {okayu_del(room.okayu, token)}"

            elif command == '名取さなしりとり':
                message_send = True
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = '名取さな'))

            elif( command == "okayu" or command == "おかゆ") and (hastoken == False):
                result += "https://shindanmaker.com/957861"
                oneshot = True

            elif (re.match('[0-9]{1,3}草粥',command)):
                message_send = True
                oneshot = True
                profile = line_bot_api.get_profile(event.source.user_id)
                okayu_up(room.okayu, profile.display_name, re.sub(r"\D", "", command))

            elif (command == "battle" and hastoken==True):
                oneshot = True
                profile = line_bot_api.get_profile(event.source.user_id)
                if token == 'everyone':
                    result += okayu_showall(room.okayu, profile.display_name)
                else:
                    if okayu_check(token) == False:
                        result += f'{token}は1d100草粥をプレイしていません!\n'
                    else:
                        result += f'{profile.display_name}({okayu_num(room.okayu, profile.display_name)}草粥) VS {token}({room.okayu, okayu_num(token)}草粥)\n'
                        if(okayu_num(room.okayu, profile.display_name)>okayu_num(token)):
                            result += f'WINNER {profile.display_name}\n'
                        elif(okayu_num(room.okayu, profile.display_name)<okayu_num(token)):
                            result += f'WINNER {token}\n'
                        else:
                            result += 'DRAW\n'

            elif command == "debug":
                message_send = True
                oneshot = True
                profile = line_bot_api.get_profile(event.source.user_id)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = room.drow_history.to_string()))
                
            elif command == "ポケポケ":
                message_send = True
                oneshot = True
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage('パック開封', get_card_img_poke())
                )

            elif command == "ドロー":
                message_send = True
                oneshot = True
                profile = line_bot_api.get_profile(event.source.user_id)
                card_url, _ = room.drow(profile.display_name)
                room.save2pkl()
                line_bot_api.reply_message(
                    event.reply_token,
                    ImageSendMessage(
                        preview_image_url=card_url,
                        original_content_url=card_url
                    )
                )
            elif command == "ドロー虫":
                message_send = True
                oneshot = True
                profile = line_bot_api.get_profile(event.source.user_id)
                card_url, _ = room.drow(profile.display_name, "437734")
                room.save2pkl()
                line_bot_api.reply_message(
                    event.reply_token,
                    ImageSendMessage(
                        preview_image_url=card_url,
                        original_content_url=card_url
                    )
                )
            elif command == "ドロー数":
                message_send = True
                oneshot = True
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage('ドロー数', room.gen_graph_json("../tools/")
                    )
                )
                
            elif command == "ドロー可愛い女":
                message_send = True
                url = random.sample(room.kawaii, 1)[0][0]
                line_bot_api.reply_message(
                    event.reply_token,
                    ImageSendMessage(
                        preview_image_url=url,
                        original_content_url=url
                    )
                )
            elif command == "かわいい":
                message_send = True
                oneshot = True
                room.kawaii.add(room.last_drowed)
                room.save2pkl()
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = f"{room.last_drowed[1]}を可愛い女デッキに追加しました！"))
                
            elif command == 'かわいくない':
                message_send = True
                if hastoken == True:
                    rm = room.rm_kawaikunai(token)
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text = "削除するカードを指定してください！"))
                    continue
                if rm != None:
                    result = f"{rm}を可愛い女デッキから削除しました！"
                else:
                    result = f"{token}は可愛い女デッキに存在しません！"
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = result))

            elif command == "デッキ":
                oneshot = True
                message_send = True
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = "https://liff.line.me/2006620823-pZ3q1a79"))

            elif command == "お絵描き":
                oneshot = True
                message_send = True
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = "https://liff.line.me/2006757163-0yxP8z7J"))
                
            elif command == "ドローかっこいいデッキ":
                message_send = True
                url = random.sample(room.kakkoii, 1)[0][0]
                line_bot_api.reply_message(
                    event.reply_token,
                    ImageSendMessage(
                        preview_image_url=url,
                        original_content_url=url
                    )
                )
            elif command == "かっこいい":
                message_send = True
                oneshot = True
                room.kakkoii.add(room.last_drowed)
                room.save2pkl()
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = f"{room.last_drowed[1]}をかっこいいデッキに追加しました！"))
                
            elif command == 'かっこよくない':
                message_send = True
                if hastoken == True:
                    rm = room.rm_kakkoyokunai(token)
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text = "削除するカードを指定してください！"))
                    continue
                if rm != None:
                    result = f"{rm}をかっこいいデッキから削除しました！"
                else:
                    result = f"{token}はかっこいいデッキに存在しません！"
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = result))

            elif command == "ドローつよそう":
                message_send = True
                url = random.sample(room.tuyosou, 1)[0][0]
                line_bot_api.reply_message(
                    event.reply_token,
                    ImageSendMessage(
                        preview_image_url=url,
                        original_content_url=url
                    )
                )

            elif command == "つよそう":
                message_send = True
                oneshot = True
                room.tuyosou.add(room.last_drowed)
                room.save2pkl()
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = f"{room.last_drowed[1]}をつよそうデッキに追加しました！"))
                
            elif command == 'つよくなさそう':
                message_send = True
                if hastoken == True:
                    rm = room.rm_tuyosou(token)
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text = "削除するカードを指定してください！"))
                    continue
                if rm != None:
                    result = f"{rm}をつよそうデッキから削除しました！"
                else:
                    result = f"{token}はつよそうデッキに存在しません！"
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = result))

            elif command == "ドローよわそう":
                message_send = True
                url = random.sample(room.yowasou, 1)[0][0]
                line_bot_api.reply_message(
                    event.reply_token,
                    ImageSendMessage(
                        preview_image_url=url,
                        original_content_url=url
                    )
                )

            elif command == "よわそう":
                message_send = True
                oneshot = True
                room.yowasou.add(room.last_drowed)
                room.save2pkl()

            elif command == 'よわくなさそう':
                message_send = True
                if hastoken == True:
                    rm = room.rm_yowasou(token)
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text = "削除するカードを指定してください！"))
                    continue
                if rm != None:
                    result = f"{rm}をよわそうデッキから削除しました！"
                else:
                    result = f"{token}はよわそうデッキに存在しません！"
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = result))

            elif command == "uno" or command == "ウノ":
                oneshot = True
                message_send = True
                if game == None:
                    game = Uno_Game(event.source.group_id)
                    make_pkl(game, f"../pkl/uno/{game.id}_uno")
                if game.status == None:
                    game = Uno_Game(event.source.group_id)
                    game.status = "JOINING"
                    make_pkl(game, f"../pkl/uno/{game.id}_uno")
                else:
                    game = Uno_Game(event.source.group_id)
                    game.status = "JOINING"
                    make_pkl(game, f"../pkl/uno/{game.id}_uno")
                    line_bot_api.push_message(game.id, TextSendMessage(text="前回のゲームを終了しました！"))
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage('UNO', gen_start_json()
                    )
                )
            elif command == "uno_join" and game.status == "JOINING":
                oneshot = True
                message_send = True
                try:
                    line_bot_api.get_profile(event.source.user_id)
                    if event.source.user_id not in game.users_raw:
                        game.users_raw.append(event.source.user_id)
                        make_pkl(game, f"../pkl/uno/{game.id}_uno")
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{line_bot_api.get_profile(event.source.user_id).display_name}さんが参加しました！"))
                    else:
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{line_bot_api.get_profile(event.source.user_id).display_name}さんは既に参加しています"))
                except:
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="友達追加してください！"))
            
            elif command == "uno_check_participant" and game.status == "JOINING":
                oneshot = True
                message_send = True
                print(game.users_raw)
                line_bot_api.reply_message(event.reply_token, FlexSendMessage('UNO', uno_check_participant([line_bot_api.get_profile(user).display_name for user in game.users_raw])))
            
            elif command == "uno_start_game" and game.status == "JOINING":
                oneshot = True
                message_send = True
                game.start()
                game.status = "START"
                make_pkl(game, f"../pkl/uno/{game.id}_uno")
                for user in game.users_raw:
                    print(user)
                    line_bot_api.push_message(user, FlexSendMessage("手札情報", gen_hand_json(game.search_user(user).hand, game)))
                line_bot_api.reply_message(event.reply_token, FlexSendMessage('UNO', gen_deck_info_json(None, line_bot_api.get_profile(game.next_user).display_name, game, [])))
            
            elif command == "reset":
                oneshot = True
                message_send = True
                game.status = None
                make_pkl(game, f"../pkl/uno/{game.id}_uno")
            
            elif re.match(".*_uno_pop_[0-9]_[0-9]{1,2}", command):
                oneshot = True
                message_send = True
                user_id = event.source.user_id
                group_id, _, _, color, num = [int(n) if n.isdigit() else n for n in command.split('_')]
                game = load_uno(group_id)
                if game.next_user == user_id  and (game.status == "START" or game.status == "color_change"):
                    if game.can_pop(color, num):
                        if game.search_user(user_id).serach_card(color, num) or game.status == "color_change":
                            if game.status == "color_change":
                                game.status = "START"
                                card = Card(color, num)
                                make_pkl(game, f"../pkl/uno/{game.id}_uno")
                            else:
                                if color == ACTION:
                                    game.status = "color_change"
                                    game.search_user(user_id).pop_card(color, num)
                                    make_pkl(game, f"../pkl/uno/{game.id}_uno")
                                    line_bot_api.reply_message(event.reply_token, FlexSendMessage("色選択", gen_choice_color_json(num, game)))
                                    break
                                card = game.search_user(user_id).pop_card(color, num)
                            if num == REVERSE: game.reverse *= -1
                            elif num == SKIP: game.turn += 1 if game.reverse == 1 else -1
                            elif num == DRAW2: game.debt += 2
                            elif num == DRAW4: game.debt += 4
                            game.trush.append(card)
                            game.prev_trush.append(card)
                            current = game.next_user
                            if len(game.search_user(current).hand) == 0:
                                game.rm_user(current)
                                if len(game.users_raw) == 1:
                                    game.rm_user(game.users_raw[0])
                                    game.status = None
                                    make_pkl(game, f"../pkl/uno/{game.id}_uno")
                                    line_bot_api.push_message(game.id, FlexSendMessage("場札情報", gen_deck_info_json(line_bot_api.get_profile(current).display_name, "line_bot_api.get_profile(next).display_name", game, [f"残り枚数: {len(game.search_user(current).hand)}"])))
                                    line_bot_api.push_message(game.id, FlexSendMessage("リザルト", gen_result_json([line_bot_api.get_profile(user).display_name for user in game.ranking])))
                                    break
                            next = game.next()
                            line_bot_api.push_message(game.id, FlexSendMessage("場札情報", gen_deck_info_json(line_bot_api.get_profile(current).display_name, line_bot_api.get_profile(next).display_name, game, [f"残り枚数: {len(game.search_user(current).hand)}"])))
                            game.prev_trush.clear()
                            make_pkl(game, f"../pkl/uno/{game.id}_uno")
                            line_bot_api.push_message(next, FlexSendMessage("手札情報", gen_hand_json(game.search_user(next).hand, game)))
                        else: line_bot_api.reply_message(event.reply_token, TextSendMessage(text="そのカードはもう所持していません！"))
                    else:
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="そのカードは捨てられません！"))
                else: line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"今はあなたのターンではありません！"))
            
            elif re.match(".*_uno_multiple_pop_[0-9]_[0-9]{1,2}", command):
                oneshot = True
                message_send = True
                user_id = event.source.user_id
                group_id, _, _, _, color, num = [int(n) if n.isdigit() else n for n in command.split('_')]
                game = load_uno(group_id)
                make_pkl(game, f"../pkl/uno/{game.id}_uno")
                if game.next_user == user_id  and (game.status == "START" or game.status == "pop_multiple"):
                    check = game.can_multiple_pop(color, num) if game.status == "pop_multiple" else game.can_pop(color, num)
                    if check and color != ACTION:
                        if game.search_user(user_id).serach_card(color, num):
                            card = game.search_user(user_id).pop_card(color, num)
                            if num == REVERSE: game.reverse *= -1
                            elif num == SKIP: game.turn += 1 if game.reverse == 1 else -1
                            elif num == DRAW2: game.debt += 2
                            elif num == DRAW4: game.debt += 4
                            game.trush.append(card)
                            game.prev_trush.append(card)
                            current = game.next_user
                            if len(game.search_user(current).hand) == 0:
                                game.rm_user(current)
                                if len(game.users_raw) == 1:
                                    game.rm_user(game.users_raw[0])
                                    game.status = None
                                    make_pkl(game, f"../pkl/uno/{game.id}_uno")
                                    line_bot_api.push_message(game.id, FlexSendMessage("リザルト", gen_result_json([line_bot_api.get_profile(user).display_name for user in game.ranking])))
                                    break
                            game.status = "pop_multiple"
                            make_pkl(game, f"uno/../pkl/{game.id}_uno")
                            line_bot_api.push_message(current, FlexSendMessage("手札情報", gen_hand_json(game.search_user(current).hand, game, 1)))
                        else: line_bot_api.reply_message(event.reply_token, TextSendMessage(text="そのカードはもう所持していません！"))
                    else:
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="そのカードは捨てられません！"))
                else: line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"今はあなたのターンではありません！"))
            
            elif re.match(".*_uno_draw_[0-9]{1,2}", command):
                oneshot = True
                message_send = True
                group_id, _, _, draw_num = [int(n) if n.isdigit() else n for n in command.split('_')]
                game = load_uno(group_id)
                if game.status != "START": break
                if draw_num != 1: game.debt = 0
                for _ in range(draw_num):
                    if len(game.deck) == 0:
                        top: Card = game.trush[-1]
                        game.deck = np.array(game.trush)
                        np.random.shuffle(game.deck)
                        game.trush.clear()
                        game.trush.append(top)
                    game.search_user(event.source.user_id).draw_card(game.deck[0])
                    game.deck = np.delete(game.deck, 0)
                line_bot_api.reply_message(event.reply_token, FlexSendMessage("手札情報", gen_hand_json(game.search_user(event.source.user_id).hand, game)))
                current = game.next_user
                next = game.next()
                make_pkl(game, f"uno/../pkl/{game.id}_uno")
                line_bot_api.push_message(next, FlexSendMessage("手札情報", gen_hand_json(game.search_user(next).hand, game)))
                line_bot_api.push_message(game.id, FlexSendMessage("場札情報", gen_deck_info_json(line_bot_api.get_profile(current).display_name, line_bot_api.get_profile(next).display_name, game, [f"{line_bot_api.get_profile(current).display_name}さんが{draw_num}枚ドローしました！", f"残り枚数: {len(game.search_user(current).hand)}"])))
            
            elif re.match(".*_uno_end_select", command):
                oneshot = True
                message_send = True
                group_id, _, _, _ = [int(n) if n.isdigit() else n for n in command.split('_')]
                game = load_uno(group_id)
                if game.status != "pop_multiple": break
                current = game.next_user
                next = game.next()
                line_bot_api.push_message(game.id, FlexSendMessage("場札情報", gen_deck_info_json(line_bot_api.get_profile(current).display_name, line_bot_api.get_profile(next).display_name, game, [f"残り枚数: {len(game.search_user(current).hand)}"])))
                game.prev_trush.clear()
                game.status = "START"
                make_pkl(game, f"../pkl/uno/{game.id}_uno")
                line_bot_api.push_message(next, FlexSendMessage("手札情報", gen_hand_json(game.search_user(next).hand, game)))
            elif re.match("https://x.com/.*", command):
                oneshot = True
                message_send = True
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = command.replace('x', 'twitter')))

            elif command == "group" and hastoken==True:
                oneshot = True
                message_send = True
                #print(names)
                command = linesplit(token)["command"]
                token = linesplit(token)["token"]
                if command == "create":
                    if token not in room.groups:
                        room.groups[token] = set()
                        room.save2pkl()
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"グループ{token}を作成しました！"))
                    else:
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"グループ{token}は既に存在します！"))

                elif command == "add":
                    command = linesplit(token)["command"]
                    token = linesplit(token)["token"]
                    users = {m.user_id for m in event.message.mention.mentionees if m.user_id != None}
                    for u in users:
                        room.groups[command].add(u)
                    room.save2pkl()
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"グループ{command}のメンバーを更新しました！"))
                elif command == "rm":
                    user = event.message.mention.mentionees[0].userid
                    name = line_bot_api.get_profile(user).display_name

            elif re.match("@.*", command):
                message_send = True
                if event.message.mention == None:
                    m = re.search(r"^@.*", command)
                    group = m.group()[1:]
                    user_ids = room.groups[group]
                    msg = ""
                    users = dict()
                    for i, u in enumerate(user_ids):
                        users[f"user{i}"] = u
                        msg += f"{{user{i}}} "
                    v2 = dict()
                    v2["type"] = "textV2"
                    v2["text"] = msg
                    v2["substitution"] = dict()
                    for user in users:
                        v2["substitution"][user] = dict()
                        v2["substitution"][user]["type"] = "mention"
                        v2["substitution"][user]["mentionee"] = dict()
                        v2["substitution"][user]["mentionee"]["type"] = "user"
                        v2["substitution"][user]["mentionee"]["userId"] = users[user]
                    print(v2)
                    line_bot_api.reply_message_v2(event.reply_token, v2)

            else:
                message_send = True
        
        #print(message_send)
        if message_send == False:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=result.strip()))
        room.save2pkl()
    except Exception as e:
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"{e.__class__.__name__}: {e}"))