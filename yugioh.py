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
        w[3] *= 15
    elif dt.weekday() == 5:
        w[4] *= 15
        w[5] *= 15
        w[6] *= 1000
    elif dt.weekday() == 6:
        categories = copy.deepcopy(categories_rare)
        mode = "rare"
        w = [0, 0, 0, 1, 0, 0, 0]
    category = random.choices(categories, weights=w)[0]
    if type != None:
        category = type

    path = f"yugioh_url/{mode}/{category}.csv"
    with open(path, "r", encoding="UTF-8") as f:
        data = list(csv.reader(f))
        size = len(data)
        index = random.randint(0, size - 1)
        return tuple(data[index])