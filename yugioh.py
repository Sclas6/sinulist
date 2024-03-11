from bs4 import BeautifulSoup as bs
from random import choice, choices
from urllib import request

def get_card_img():
    url_base = "https://game8.jp/yugioh-masterduel/"
    categories = [
        "437764", #UR
        "437766", #SR
        "437767", #R
        "437768", #N
        "437656", #NG
        "437693", #Limited
        "437715"  #Semi-Limited
    ]

    categories_limited = [
        "437656", #NG
        "437693", #Limited
        "437715"  #Semi-Limited
    ]
    w = [835, 1936, 3385, 4862, 86, 66, 44]

    category = choices(categories, weights=w)[0]
    #category = choice(categories)
    url = f"{url_base}{category}"
    #print(url)

    #for category in categories:
    #    url = f"{url_base}{category}"
    response = request.urlopen(url)
    soup = bs(response, "lxml")
    image_url = set()
    if category in categories_limited:
        a = soup.find_all(class_="a-table a-table a-table")
        if category == "437656":
            b = a[1]
        else:
            b = a[0]
        c = choice(b.find_all(class_="a-link"))
        url = c.get("href")
        #print(url)
        response = request.urlopen(url)
        soup = bs(response, "lxml")
        d = soup.find(class_="a-table a-table a-table")
        e = d.find(class_="center")
        return e.find(class_='a-img lazy lazy-non-square').get("data-src")
        #with open("img_url.txt", 'a') as f:
        #    f.write(f"{e.find(class_='a-img lazy lazy-non-square').get('data-src')}\n")
    else:
        while True:
            try:
                a = choice(soup.find_all(class_="a-table a-table a-table"))
                b = choice(a.find_all(class_="a-link"))
            except Exception as e:
                continue
            break
        url = b.get("href")
        #print(url)
        response = request.urlopen(url)
        soup = bs(response, "lxml")
        c = soup.find(class_="a-table a-table a-table")
        d = c.find(class_="center")
        return d.find(class_='a-img lazy lazy-non-square').get("data-src")