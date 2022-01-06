from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, JoinEvent
)
from linebot.models.messages import ImageMessage
from linebot.models.send_messages import ImageSendMessage
from requests_oauthlib import OAuth1Session
import os
import time
import requests
import dropbox
import pickle
import twitter

app = Flask(__name__)

ACCESS_TOKEN=''
client=dropbox.Dropbox(ACCESS_TOKEN)

with open("list.pkl", "wb") as f:
    metadata, res = client.files_download(path="/list.pkl")
    f.write(res.content)

with open("kaita.pkl", "wb") as f:
    pass
    metadata, res = client.files_download(path="/kaita.pkl")
    f.write(res.content)

T_API_KEY=''
T_API_SEC=''
T_ACC_TOKEN=''
T_ACC_SEC=''
auth = twitter.OAuth(consumer_key=T_API_KEY,
                    consumer_secret=T_API_SEC,
                    token=T_ACC_TOKEN,
                    token_secret=T_ACC_SEC)
t = twitter.Twitter(auth=auth)
tweetId='1335593079059873795'

pic_save_availavle=False
kaitamono=''
sinulist=[]
kaitalist={}


def debug_pic1224():
    with open('kaita.pkl','wb') as f:
        pickle.dump(kaitalist,f)
    with open('kaita.pkl','rb') as f:
        client.files_upload(f.read(),'/kaita.pkl')

def checkls(kakumono):
    global sinulist
    juuhuku=False
    for n in range(len(sinulist)):
        if kakumono == sinulist[n]:
            juuhuku=True
    if juuhuku==True:
        return True
    else:
        return False

def addlist(kakumono):
    global sinulist
    if os.path.exists('list.pkl'):
        with open('list.pkl','rb') as f:
            sinulist=pickle.load(f)
    sinulist.append(kakumono)
    with open('list.pkl','wb') as f:
        pickle.dump(sinulist,f)
    with open('list.pkl','rb') as f:
        client.files_delete('/list.pkl')
        client.files_upload(f.read(),'/list.pkl')

def pic_checkls(content):
    global kaitalist
    for n in kaitalist:
        if content==n:
            return True
    return False

def pic_save(kaitamono,content):
    global kaitalist
    if os.path.exists('kaita.pkl'):
        with open('kaita.pkl','rb') as f:
            kaitalist=pickle.load(f)
    with open(f'{kaitamono}.jpg','wb') as f:
        for chunk in content.iter_content():
            f.write(chunk)
    #upload
    with open(f'{kaitamono}.jpg','rb') as f:
        client.files_upload(f.read(),f'/{kaitamono}.jpg',mode=dropbox.files.WriteMode.overwrite)
    #create link
    setting = dropbox.sharing.SharedLinkSettings(requested_visibility=dropbox.sharing.RequestedVisibility.public)
    link = client.sharing_create_shared_link_with_settings(path=f'/{kaitamono}.jpg', settings=setting)
    #get link
    links=client.sharing_list_shared_links(path=f'/{kaitamono}.jpg',direct_only=True).links
    if links is not None:
        for link in links:
            url=link.url
            url=url.replace('www.dropbox','dl.dropboxusercontent').replace('?dl=0','')
    kaitalist[kaitamono]=url
    with open('kaita.pkl','wb') as f:
        pickle.dump(kaitalist,f)
    with open('kaita.pkl','rb') as f:
        client.files_delete('/kaita.pkl')
        client.files_upload(f.read(),'/kaita.pkl')

def pic_print():
    global kaitalist
    with open('kaita.pkl','rb') as f:
        kaitalist=pickle.load(f)
    string=''
    tmp=True
    for n in kaitalist:
        if tmp==True:
            string+='  ･{0}'.format(n)
            tmp=False
        else:
            string+='\n  ･{0}'.format(n)
    return string

def pic_showpic(content):
    global kaitalist
    if os.path.exists('kaita.pkl'):
        with open('kaita.pkl','rb') as f:
            kaitalist=pickle.load(f)
    return kaitalist[content]

def pic_rmlist(kesumono):
    global kaitalist
    if os.path.exists('kaita.pkl'):
        with open('kaita.pkl','rb') as f:
            kaitalist=pickle.load(f)
    kaitalist.pop(kesumono)
    with open('kaita.pkl','wb') as f:
        pickle.dump(kaitalist,f)
    with open('kaita.pkl','rb') as f:
        client.files_delete('/kaita.pkl')
        client.files_upload(f.read(),'/kaita.pkl')
        client.files_delete(f'/{kesumono}.jpg')

def printlist():
    global sinulist
    with open('list.pkl','rb') as f:
        sinulist=pickle.load(f)
    #string='{0}'.format(sinulist)
    string=''
    for n in range(len(sinulist)):
        if n==0:
            string+='  ･{0}'.format(sinulist[n])
        else:
            string+='\n  ･{0}'.format(sinulist[n])
    return string

def rmlist(kakumono):
    global sinulist
    if os.path.exists('list.pkl'):
        with open('list.pkl','rb') as f:
            sinulist=pickle.load(f)
    sinulist.remove(kakumono)
    with open('list.pkl','wb') as f:
        pickle.dump(sinulist,f)
    with open('list.pkl','rb') as f:
        client.files_delete('/list.pkl')
        client.files_upload(f.read(),'/list.pkl')

def rmrecent():
    global sinulist
    if os.path.exists('list.pkl'):
        with open('list.pkl','rb') as f:
            sinulist=pickle.load(f)
    str=sinulist[-1]
    rmlist(sinulist[-1])
    return str

def rmnum(num):
    global sinulist
    if os.path.exists('list.pkl'):
        with open('list.pkl','rb') as f:
            sinulist=pickle.load(f)
    str=sinulist[num-1]
    rmlist(sinulist[num-1])
    return str

def commandsplit(line):
    commandlist=line.splitlines()
    return commandlist

def linesplit(commandlist):
    pc = commandlist.split()
    tokenCount=len(pc)
    command=pc[0]
    token=''
    for n in range(len(pc)):
        if n==0:
            pass
        elif n!=len(pc)-1:
            token+='{0} '.format(pc[n])
        else:
            token+='{0}'.format(pc[n])
    line={'command':command,'token':token}
    return line

        #TWITTER_API
def createTweet(kakumono):
    status='@hyorohyoro66 {0}'.format(kakumono)
    data=t.statuses.update(status=status,in_reply_to_status_id=tweetId)
    time.sleep(5)
    #print(data['id_str'])
    url = "https://api.twitter.com/1.1/favorites/create.json"
    api=OAuth1Session(T_API_KEY,T_API_SEC,T_ACC_TOKEN,T_ACC_SEC)
    id=data['id_str']
    params={'id':id}
    api.post(url,params=params)

def destroyTweet(id):
    t.statuses.destroy(id=id)

def remDestroy(kesumono):
    for tweet in t.favorites.list(screen_name='sinulist',count=200):
        tweet_obj=tweet
        if 'hyorohyoro66' in str(tweet_obj):
            #print(tweet_obj['text'])
            if kesumono in str(tweet_obj):
                try:
                    destroyTweet(tweet_obj['id'])
                except:
                    pass
        else:
            pass

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

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
    str_join='I am @hyorohyoro66 !!!!!!!'
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(str_join))

@handler.add(MessageEvent,message=ImageMessage)
def handle_image(event):
    global pic_save_availavle
    global kaitamono
    text=''
    if pic_save_availavle==True:
        message_id=event.message.id
        messege_content=line_bot_api.get_message_content(message_id)
        pic_save(kaitamono,messege_content)
        pic_save_availavle=False
        text=f'{kaitamono}を保存しました!'
        line_bot_api.push_message(event.source.group_id,TextSendMessage(text))
        remDestroy(kaitamono)
        rmlist(kaitamono)
        text='死ぬまでには描くものリストから{0}を削除しました!'.format(kaitamono)
        line_bot_api.push_message(event.source.group_id,TextSendMessage(text))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    result=''
    oneshot=False
    message_send=False
    global pic_save_availavle
    global kaitamono
    linelist=commandsplit(event.message.text)
    while len(linelist)!=0 and oneshot==False:
        line=linelist.pop(0)
        comset=linesplit(line)
        command=comset['command']
        token=comset['token']
        hastoken=False if token=='' else True
        isNotCommand=False

        #groupid=line_bot_api.get_profile(event.source.group_id)

        if (command=='show' or command=='死ぬまでには描くものリスト'):
            oneshot=True
            result+='死ぬまでには描くものリスト\n(クオリティは問わないものとする)\n{0}\n'.format(printlist())

        elif command=='add' and hastoken==True:
            kakumono=token
            if checkls(kakumono)==True:
                result+='{0}は既に存在しています!\n'.format(kakumono)
            else:
                result+='死ぬまでには描くものリストに{0}を追加しました!\n'.format(kakumono)
                status='@hyorohyoro66 {0}'.format(token)
                createTweet(kakumono)
                addlist(kakumono)
        elif command=='remove' or command=='delete' or command=='rm':
            if hastoken==True:
                try:
                    if token.isdecimal()==True:
                        tokennum=int(token)
                        kesumono=rmnum(tokennum)
                        str='死ぬまでには描くものリストから{0}を削除しました!\n'.format(kesumono)
                        remDestroy(kesumono)
                    else:
                        kesumono=token
                        str='死ぬまでには描くものリストから{0}を削除しました!\n'.format(kesumono)
                        remDestroy(kesumono)
                        rmlist(kesumono)
                except ValueError as error:
                    str='{0}は存在しません!\n'.format(kesumono)
                result+=str
            else:
                oneshot=True
                kesumono=rmrecent()
                str='死ぬまでには描くものリストから{0}を削除しました!\n'.format(kesumono)
                remDestroy(kesumono)
                result+=str
    #Picture Command
        elif command=='plist' or command=='picls' or command=='pshow':
            oneshot=True
            result+='描いたものリスト\n{0}\n'.format(pic_print())
        elif (command=='save' or command=='comp' or command=='complete') and hastoken==True:
            #oneshot=True
            if checkls(token)==False:
                result+='{0}は死ぬまでに描くものリストに存在しません!\n'.format(token)
            else:
                if pic_checkls(token)==True:
                    result+='{0}は既に存在しています!\n'.format(token)
                else:
                    pic_save_availavle=True
                    kaitamono=token
                    result+='{0}を保存します!\n画像を送信して下さい\n'.format(token)
        elif (command=='pic' or command=='showpic') and hastoken==True:
            oneshot=True
            haserror=False
            try:
                url=pic_showpic(token)
            except KeyError as error:
                result+='{0}は存在しません!\n'.format(token)
                haserror=True
            if haserror!=True:
                message_send=True
                line_bot_api.reply_message(
                    event.reply_token,
                    ImageSendMessage(
                        preview_image_url=url,
                        original_content_url=url
                    )
                )
        elif (command=='prm' or command=='pdelete' or command=='premove' or command=='picrm')and hastoken==True:
            if pic_checkls(token)==True:
                pic_rmlist(token)
                result+='{0}の画像を削除しました!\n'.format(token)
            else:
                result+='{0}は存在しません!\n'.format(token)
        elif command=='debug':
                #debug_pic1224()
                pass

        elif command=='名取さなしりとり':
            message_send=True
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage('名取さな'))

        elif command=='test':
            kakumono=token
            '''
            payload={'value1':'@hyorohyoro66 \n{0}'.format(token)}
            requests.post(WEB_HOOK_URL,data=payload)
            '''
            message_send=True
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(event.source.group_id))

        else:
            isNotCommand=True

    if isNotCommand==False and message_send==False:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(result.strip()))

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
