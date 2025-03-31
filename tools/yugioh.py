from bs4 import BeautifulSoup as bs
import random
from urllib import request
import datetime
import copy
import csv

categories_rare = [
    "437764", #UR
    "437766", #SR
    "437767", #R
    "437768", #N
    "437656", #NG
    "437693", #Limited
    "437715"  #Semi-Limited
]
categories_type = [
    "437535", #fire
    "437564", #water
    "437585", #wind
    "437586", #earth
    "437588", #light
    "437593", #dark
    "437595", #god
    '426293', #trap
    '426292', #magic
    "437656", #NG
    "437693", #Limited
    "437715"  #Semi-Limited
]

def get_card_img(type = None):
    url_base = "https://game8.jp/yugioh-masterduel/"
    categories_limited = [
        "437656", #NG
        "437693", #Limited
        "437715"  #Semi-Limited
    ]
    dt = datetime.datetime.now()
    w = [612, 746, 705, 1739, 1479, 1999, 5, 1645, 2102, 86, 66, 44]
    categories = copy.deepcopy(categories_type)
    if dt.weekday() == 0:
        categories = copy.deepcopy(categories_rare)
        #w = [0, 0, 0, 1, 0, 0, 0]
        w = [50, 0, 0, 0, 86, 66, 44]
    elif dt.weekday() == 1:
        w[0] *= 15
    elif dt.weekday() == 2:
        w[1] *= 15
    elif dt.weekday() == 3:
        w[2] *= 15
    elif dt.weekday() == 4:
        w[3] *= 15
    elif dt.weekday() == 5:
        w[4] *= 15
        w[5] *= 15
        w[6] *= 1000
    elif dt.weekday() == 6:
        categories = copy.deepcopy(categories_rare)
        w = [0, 0, 0, 1, 0, 0, 0]
    category = random.choices(categories, weights=w)[0]
    if type != None:
        category = type
    url = f"{url_base}{category}"
    response = request.urlopen(url)
    soup = bs(response, "lxml")
    image_url = set()
    if category in categories_limited:
        a = soup.find_all(class_="a-table a-table a-table")
        if category == "437656":
            b = a[1]
        else:
            b = a[0]
        c = random.choice(b.find_all(class_="a-link"))
        url = c.get("href")
        response = request.urlopen(url)
        soup = bs(response, "lxml")
        title = soup.find('title').text[10:-21]
        d = soup.find(class_="a-table a-table a-table")
        e = d.find(class_="center")
        return e.find(class_='a-img lazy lazy-non-square').get("data-src"), title
    else:
        while True:
            try:
                a = random.choice(soup.find_all(class_="a-table a-table a-table"))
                b = random.choice(a.find_all(class_="a-link"))
            except Exception as e:
                continue
            break
        url = b.get("href")
        response = request.urlopen(url)
        soup = bs(response, "lxml")
        title = soup.find('title').text[10:-21]
        print(title)
        c = soup.find(class_="a-table a-table a-table")
        d = c.find(class_="center")
        return d.find(class_='a-img lazy lazy-non-square').get("data-src"), title

def get_card_img_2(type = None):
    dt = datetime.datetime.now()
    w = [612, 746, 705, 1739, 1479, 1999, 5, 1645, 2102, 86, 66, 44]
    categories = copy.deepcopy(categories_type)
    mode = "type"
    category = None
    if dt.weekday() == 0:
        categories = copy.deepcopy(categories_rare)
        mode = "rare"
        w = [50, 0, 0, 0, 86, 66, 44]
    elif dt.weekday() == 1:
        w[0] *= 15
    elif dt.weekday() == 2:
        w[1] *= 15
    elif dt.weekday() == 3:
        w[2] *= 15
    elif dt.weekday() == 4:
        "w[3] *= 15"
        mode = "other"
        category = "437616"
    elif dt.weekday() == 5:
        w[4] *= 15
        w[5] *= 15
        w[6] *= 1000
    elif dt.weekday() == 6:
        categories = copy.deepcopy(categories_rare)
        mode = "rare"
        w = [0, 0, 0, 1, 0, 0, 0]
    if category is None:
        category = random.choices(categories, weights=w)[0]
    if type != None:
        category = type

    path = f"yugioh_url/{mode}/{category}.csv"
    with open(path, "r", encoding="UTF-8") as f:
        data = list(csv.reader(f))
        size = len(data)
        index = random.randint(0, size - 1)
        return tuple(data[index])

def gen_poke_json(urls: list):
    carousel = dict()
    carousel["type"] = "carousel"
    carousel["contents"] = list()
    for url in urls:
        content = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": url,
                "size": "full",
                "position": "relative",
                "aspectRatio": "311:440"
            }
        }
        carousel["contents"].append(content)
    return carousel

def get_card_img_poke():
    is_god = True if random.randint(1, 100000) <= 50 else False
    categories = ["645035", "645036", "645037", "645038", "645039", "645040", "645041", "645042"]
    w = [[100, 0, 0, 0, 0, 0, 0, 0],
         [100, 0, 0, 0, 0, 0, 0, 0],
         [100, 0, 0, 0, 0, 0, 0, 0],
         [0, 90000, 5000, 1666, 2572, 500, 222, 40],
         [0, 60000, 20000, 6664, 10288, 2000, 888, 160]]
    urls = []
    for i in range(5):
        if is_god:
            weight = [0, 0, 0, 0, 40, 50, 5, 5]
        else:
            weight = w[i]
        category = random.choices(categories, weights=weight)[0]
        path = f"csv_poke/{category}.csv"
        with open(path, "r", encoding="UTF-8") as f:
            data = list(csv.reader(f))
            size = len(data)
            index = random.randint(0, size - 1)
            urls.append(data[index][0])
    return gen_poke_json(urls)