import twitter
import requests
import time
from requests_oauthlib import OAuth1Session

T_API_KEY='zf6sngMdfdVI2zh2sQNrNtv0Q'
T_API_SEC='Naf6Tsq2BvigA0hEArogzzbzlAtEy0oQGXhluUCJvCRSgOTFOg'
T_ACC_TOKEN='757848958626476032-8KWFB8PIjHwKMkdjjVu72QZIMtxPN5U'
T_ACC_SEC='pFi5zUjgncX9891r5SEPrKinoHXHw1zsXT5qBLJJZKHXQ'

auth = twitter.OAuth(consumer_key=T_API_KEY,
                    consumer_secret=T_API_SEC,
                    token=T_ACC_TOKEN,
                    token_secret=T_ACC_SEC)

t = twitter.Twitter(auth=auth)
tweetId='1335593079059873795'

def createTweet(kakumono):
    status='hyorohyoro66 {0}'.format(kakumono)
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
            print(tweet_obj['text'])
            if kesumono in str(tweet_obj):
                try:
                    destroyTweet(tweet_obj['id'])
                except:
                    pass
        else:
            pass
