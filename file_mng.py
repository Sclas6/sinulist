import bs4
import datetime
from matplotlib import pyplot as plt
import japanize_matplotlib
import os
import pickle
import pandas as pd
import time
import uuid
import yugioh

class Room():
    def __init__(self):
        self.sinulist = dict()
        self.kaitamono = ""
        self.kaitalist = dict()
        self.okayu = dict()
        self.memo = ""
        self.counter = Counter()
        self.pic_save_availavle = False
        self.last_drowed = None
        self.kawaii = set()
        self.kakkoii = set()
        self.tuyosou = set()
        self.yowasou = set()
        self.drow_history = None

    def save2pkl(self):
        with open("RoomInfo.pkl", "wb") as f:
            pickle.dump(self, f)

    def rm_kawaikunai(self, name: str):
        for card in self.kawaii:
            if card[1] == name:
                self.kawaii.remove(card)
                self.save2pkl()
                return name
        return None

    def rm_kakkoyokunai(self, name: str):
        for card in self.kakkoii:
            if card[1] == name:
                self.kakkoii.remove(card)
                self.save2pkl()
                return name
        return None

    def rm_tuyosou(self, name: str):
        for card in self.tuyosou:
            if card[1] == name:
                self.tuyosou.remove(card)
                self.save2pkl()
                return name
        return None

    def rm_yowasou(self, name: str):
        for card in self.yowasou:
            if card[1] == name:
                self.yowasou.remove(card)
                self.save2pkl()
                return name
        return None

    def drow(self, name: str, category: str=None):
        card = yugioh.get_card_img_2(category)
        now = datetime.datetime.now()
        self.counter.add_user(name)
        self.last_drowed = card

        lasttime_drowed = pd.Timestamp(self.drow_history.index.values[-1])
        now = datetime.datetime.now()
        if (now - lasttime_drowed)/datetime.timedelta(days=1) > 1:
            df_new = pd.DataFrame(self.counter.counter, index=[now])
            self.drow_history = pd.concat([self.drow_history, df_new])
        return card

    def gen_graph_json(self):
        df: pd.DataFrame = self.drow_history
        """for i, date in enumerate(reversed(df.index)):
            if (df.index[-1] - date) / datetime.timedelta(days=1) > 1:
                yesterday = i
                break
        df_week = df[-yesterday:]
        df_week.plot()
        img_name_week = str(time.time()).replace('.', '').ljust(17, '0')
        images = [file for file in sorted(os.listdir("img"), reverse=True) if file[:4] == "drow"]
        for i, file in enumerate(images):
            if i >= 4: os.remove(f"img/{file}")
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0, fontsize=18)
        plt.savefig(f"img/drow_{img_name_week}.png", bbox_inches='tight')"""
        df_all = df
        df_all.plot()
        img_name_all = str(time.time()).replace('.', '').ljust(17, '0')
        images = [file for file in sorted(os.listdir("img"), reverse=True) if file[:4] == "drow"]
        for i, file in enumerate(images):
            if i >= 4: os.remove(f"img/{file}")
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0, fontsize=18)
        plt.savefig(f"img/drow_{img_name_all}.png", bbox_inches='tight')
        df_diff = df.diff(periods=7)[-7:]
        df_diff.plot.barh()
        img_name_diff = str(time.time()).replace('.', '').ljust(17, '0')
        images = [file for file in sorted(os.listdir("img"), reverse=True) if file[:4] == "drow"]
        for i, file in enumerate(images):
            if i >= 4: os.remove(f"img/{file}")
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0, fontsize=18)
        plt.savefig(f"img/drow_{img_name_diff}.png", bbox_inches='tight')
        content = {
            "type": "carousel",
                "contents": [
                    {
                    "type": "bubble",
                    "header": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "text",
                            "text": "ドロー増減数",
                            "size": "xl",
                            "weight": "bold",
                            "align": "center"
                        }
                        ]
                    },
                    "hero": {
                        "type": "image",
                        "url": f"https://sclas.xyz/img/drow_{img_name_diff}.png",
                        "size": "full",
                        "aspectMode": "fit",
                        "aspectRatio": "20:10"
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "text",
                            "text": self.counter.gen_info(),
                            "size": "md",
                            "wrap": True
                        }
                        ]
                    }
                    },
                    {
                    "type": "bubble",
                    "header": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "text",
                            "text": "ドロー総数",
                            "size": "xl",
                            "weight": "bold",
                            "align": "center"
                        }
                        ]
                    },
                    "hero": {
                        "type": "image",
                        "url": f"https://sclas.xyz/img/drow_{img_name_all}.png",
                        "size": "full",
                        "aspectMode": "fit",
                        "aspectRatio": "20:10"
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "text",
                            "text": self.counter.gen_info(),
                            "size": "md",
                            "wrap": True
                        }
                        ]
                    }
                    }
                ]
        }
        return content

    def gen_onnna_json(self):
        soup = bs4.BeautifulSoup("<!DOCTYPE HTML>", 'html.parser')

        tag_html = soup.new_tag("html")
        tag_head = soup.new_tag("head")
        tag_meta = soup.new_tag("meta")
        tag_meta["charset"] = "UTF-8"
        tag_meta["http-equiv"] = "Cache-Control"
        tag_meta["content"] = "no-store"
        tag_title = soup.new_tag("title")
        tag_title.string = "可愛い女デッキ"
        tag_body = soup.new_tag("body")

        soup.append(tag_html)
        soup.html.append(tag_head)
        soup.html.head.append(tag_meta)
        soup.html.head.append(tag_title)
        soup.html.append(tag_body)
        for card in self.kawaii:
            tag_img = soup.new_tag("img")
            tag_img["src"] = card[0]
            soup.html.body.append(tag_img)
        return str(soup)

    def gen_kakkoii_json(self):
        soup = bs4.BeautifulSoup("<!DOCTYPE HTML>", 'html.parser')

        tag_html = soup.new_tag("html")
        tag_head = soup.new_tag("head")
        tag_meta = soup.new_tag("meta")
        tag_meta["charset"] = "UTF-8"
        tag_meta["http-equiv"] = "Cache-Control"
        tag_meta["content"] = "no-store"
        tag_title = soup.new_tag("title")
        tag_title.string = "かっこいいデッキ"
        tag_body = soup.new_tag("body")

        soup.append(tag_html)
        soup.html.append(tag_head)
        soup.html.head.append(tag_meta)
        soup.html.head.append(tag_title)
        soup.html.append(tag_body)
        for card in self.kakkoii:
            tag_img = soup.new_tag("img")
            tag_img["src"] = card[0]
            soup.html.body.append(tag_img)
        return str(soup)

    def gen_tuyosou_json(self):
        soup = bs4.BeautifulSoup("<!DOCTYPE HTML>", 'html.parser')

        tag_html = soup.new_tag("html")
        tag_head = soup.new_tag("head")
        tag_meta = soup.new_tag("meta")
        tag_meta["charset"] = "UTF-8"
        tag_meta["http-equiv"] = "Cache-Control"
        tag_meta["content"] = "no-store"
        tag_title = soup.new_tag("title")
        tag_title.string = "つよそうデッキ"
        tag_body = soup.new_tag("body")

        soup.append(tag_html)
        soup.html.append(tag_head)
        soup.html.head.append(tag_meta)
        soup.html.head.append(tag_title)
        soup.html.append(tag_body)
        for card in self.tuyosou:
            tag_img = soup.new_tag("img")
            tag_img["src"] = card[0]
            soup.html.body.append(tag_img)
        return str(soup)

    def gen_yowasou_json(self):
        soup = bs4.BeautifulSoup("<!DOCTYPE HTML>", 'html.parser')

        tag_html = soup.new_tag("html")
        tag_head = soup.new_tag("head")
        tag_meta = soup.new_tag("meta")
        tag_meta["charset"] = "UTF-8"
        tag_meta["http-equiv"] = "Cache-Control"
        tag_meta["content"] = "no-store"
        tag_title = soup.new_tag("title")
        tag_title.string = "よわそうデッキ"
        tag_body = soup.new_tag("body")

        soup.append(tag_html)
        soup.html.append(tag_head)
        soup.html.head.append(tag_meta)
        soup.html.head.append(tag_title)
        soup.html.append(tag_body)
        for card in self.yowasou:
            tag_img = soup.new_tag("img")
            tag_img["src"] = card[0]
            soup.html.body.append(tag_img)
        return str(soup)


class Counter:
    def __init__(self):
        self.counter = {}

    def add_user(self, id_user):
        if id_user not in self.counter:
            self.counter[id_user] = [1]
        else:
            self.counter[id_user][0] += 1

    def gen_info(self):
        text = ""
        dict_sorted = sorted(self.counter.items(), key=lambda x:x[1], reverse=True)
        for i, c in enumerate(dict_sorted):
            if i == len(dict_sorted) - 1:
                text += f"{i + 1}位: {c[0]} {c[1][0]}回"
            else:
                text += f"{i + 1}位: {c[0]} {c[1][0]}回\n"
        return text

def make_pkl(var, name):
        with open(f"{name}.pkl", "wb") as f:
            pickle.dump(var, f)

def organize_files():
    files = os.listdir("img")
    for i, file in enumerate(sorted(files, reverse = True)):
        #if i >= 10: os.remove(f"img/{file}")
        pass