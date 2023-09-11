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
from uno import *
from uno_json import *

app = Flask(__name__)

pic_save_availavle = False
kaitamono = ""
memo = ""
sinulist = []
kaitalist = {}
okayu = {}
game = None

def loadfiles():
    global sinulist, kaitalist, okayu, memo, game
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
    if os.path.exists('uno.pkl'):
        with open('uno.pkl','rb') as f:
            game = pickle.load(f)

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
    global game
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

        elif command == "uno" or command == "ウノ":
            oneshot = True
            message_send = True
            if game == None:
                game = Uno_Game(event.source.group_id)
            if game.status == None:
                game = Uno_Game(event.source.group_id)
                game.status = "JOINING"
                make_pkl(game, "uno")
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage('UNO', gen_start_json()
                    )
                )
            else:
                game = Uno_Game(event.source.group_id)
                game.status = "JOINING"
                make_pkl(game, "uno")
                line_bot_api.push_message(game.id, TextSendMessage("前回のゲームを終了しました！"))
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
                    make_pkl(game, "uno")
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(f"{line_bot_api.get_profile(event.source.user_id).display_name}さんが参加しました！"))
                else:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(f"{line_bot_api.get_profile(event.source.user_id).display_name}さんは既に参加しています"))
            except:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage("友達追加してください！"))
        
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
            make_pkl(game, "uno")
            for user in game.users_raw:
                print(user)
                line_bot_api.push_message(user, FlexSendMessage("手札情報", gen_hand_json(game.search_user(user).hand, game)))
            line_bot_api.reply_message(event.reply_token, FlexSendMessage('UNO', gen_deck_info_json(None, line_bot_api.get_profile(game.next_user).display_name, game, [])))
        
        elif command == "reset":
            oneshot = True
            message_send = True
            game.status = None
            make_pkl(game, "uno")
        
        elif re.match("uno_pop_[0-9]_[0-9]{1,2}", command) and (game.status == "START" or game.status == "color_change"):
            oneshot = True
            message_send = True
            user_id = event.source.user_id
            print(game.next_user)
            if game.next_user == user_id:
                color, num = [int(n) for n in re.findall(r"\d+", command)]
                if game.can_pop(color, num):
                    if game.search_user(user_id).serach_card(color, num) or game.status == "color_change":
                        if game.status == "color_change":
                            game.status = "START"
                            card = Card(color, num)
                            make_pkl(game, "uno")
                        else:
                            if color == ACTION:
                                game.status = "color_change"
                                game.search_user(user_id).pop_card(color, num)
                                make_pkl(game, "uno")
                                line_bot_api.reply_message(event.reply_token, FlexSendMessage("色選択", gen_choice_color_json(num)))
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
                                game.status == None
                                make_pkl(game, "uno")
                        next = game.next()
                        line_bot_api.push_message(game.id, FlexSendMessage("場札情報", gen_deck_info_json(line_bot_api.get_profile(current).display_name, line_bot_api.get_profile(next).display_name, game, [f"残り枚数: {len(game.search_user(current).hand)}"])))
                        game.prev_trush.clear()
                        make_pkl(game, "uno")
                        line_bot_api.push_message(next, FlexSendMessage("手札情報", gen_hand_json(game.search_user(next).hand, game)))
                    else: line_bot_api.reply_message(event.reply_token, TextSendMessage("そのカードはもう所持していません！"))
                else:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage("そのカードは捨てられません！"))
            else: line_bot_api.reply_message(event.reply_token, TextSendMessage(f"今はあなたのターンではありません！"))
        
        elif re.match("uno_multiple_pop_[0-9]_[0-9]{1,2}", command) and (game.status == "START" or game.status == "pop_multiple"):
            oneshot = True
            message_send = True
            user_id = event.source.user_id
            print(game.next_user)
            make_pkl(game, "uno")
            if game.next_user == user_id:
                color, num = [int(n) for n in re.findall(r"\d+", command)]
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
                                game.status == None
                                make_pkl(game, "uno")
                                line_bot_api.push_message(game.id, FlexSendMessage("リザルト", gen_result_json([line_bot_api.get_profile(user).display_name for user in game.ranking])))
                                break
                        game.status = "pop_multiple"
                        make_pkl(game, "uno")
                        line_bot_api.push_message(current, FlexSendMessage("手札情報", gen_hand_json(game.search_user(current).hand, game, 1)))
                    else: line_bot_api.reply_message(event.reply_token, TextSendMessage("そのカードはもう所持していません！"))
                else:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage("そのカードは捨てられません！"))
            else: line_bot_api.reply_message(event.reply_token, TextSendMessage(f"今はあなたのターンではありません！"))
        
        elif re.match("uno_draw_[0-9]{1,2}", command) and game.status == "START":
            oneshot = True
            message_send = True
            draw_num, = [int(n) for n in re.findall(r"\d+", command)]
            if draw_num != 1: game.debt = 0
            for _ in range(draw_num):
                game.search_user(event.source.user_id).draw_card(game.deck[0])
                game.deck = np.delete(game.deck, 0)
            line_bot_api.reply_message(event.reply_token, FlexSendMessage("手札情報", gen_hand_json(game.search_user(event.source.user_id).hand, game)))
            current = game.next_user
            next = game.next()
            make_pkl(game, "uno")
            line_bot_api.push_message(next, FlexSendMessage("手札情報", gen_hand_json(game.search_user(next).hand, game)))
            line_bot_api.push_message(game.id, FlexSendMessage("場札情報", gen_deck_info_json(line_bot_api.get_profile(current).display_name, line_bot_api.get_profile(next).display_name, game, [f"{line_bot_api.get_profile(current).display_name}さんが{draw_num}枚ドローしました！", f"残り枚数: {len(game.search_user(current).hand)}"])))
        
        elif command == "uno_end_select" and game.status == "pop_multiple":
            oneshot = True
            message_send = True
            current = game.next_user
            next = game.next()
            line_bot_api.push_message(game.id, FlexSendMessage("場札情報", gen_deck_info_json(line_bot_api.get_profile(current).display_name, line_bot_api.get_profile(next).display_name, game, [f"残り枚数: {len(game.search_user(current).hand)}"])))
            game.prev_trush.clear()
            game.status = "START"
            make_pkl(game, "uno")
            line_bot_api.push_message(next, FlexSendMessage("手札情報", gen_hand_json(game.search_user(next).hand, game)))

    if isNotCommand == True and message_send == False:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(result.strip()))