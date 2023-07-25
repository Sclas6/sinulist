from bs4 import BeautifulSoup as bs
import datetime
from file_mng import *
import japanize_matplotlib
import json
import matplotlib.pyplot as plt
import pandas as pd
import re
import requests
import time

def gen_score_json(team):
    if team == "dragons":
        data = gen_dragons_info()
    elif team == "mlb_angels":
        data = gen_mlb_info("angels")
    elif team == "mlb_dodgers":
        data = gen_mlb_info("dodgers")
    else : data = gen_dragons_info()
    content = '{"type": "bubble","hero": {"type":"box","layout":"vertical","contents":[{"type": "image","url": '
    content += f'"{data["url"]}"'
    content +=  ',"size": "full","aspectRatio": "5:1","aspectMode": "cover"}],"height":"68px","backgroundColor": '
    content += f'"{data["color"]}"'
    content += '},"body": {"type": "box","layout": "vertical","contents": [{"type": "text","text":'
    content += f'"{data["teams"]}"'
    content += ',"weight": "bold","size": "xl"},{"type": "box","layout": "vertical","margin": "md","contents": [{"type": "text","text": '
    content += f'"{data["data"]}"'
    content += '},{"type": "text","text": '
    content += f'"{data["status"]}"'
    content += ',"size": "sm","color": "#999999","margin": "md","flex": 0}]},{"type": "box","layout": "vertical","margin": "lg","spacing": "sm","contents": [{"type": "box","layout": "baseline","spacing": "sm","contents": [{"type": "text","text": "経過","color": "#aaaaaa","size": "sm","flex": 1},{"type": "text","text": '
    content += f'"{data["now"]}"'
    content += ',"wrap": true,"color": "#666666","size": "sm","flex": 5}]}]}]}}'
    return json.loads(content)

def gen_mlb_info(team):
    load_url = f"https://www.mlb.com/{team}/scores"
    html = requests.get(load_url)
    soup = bs(html.content, "html.parser")
    score_data = soup.find(class_ = re.compile('^tablestyle__StyledTable'))

    teams = [element.text for i, element in enumerate(soup.find_all(class_ = re.compile('^TeamWrappersstyle__DesktopTeamWrapper'))) if i < 2]
    score_team_1 = [(int)(element.text) for element in score_data.find_all(id = re.compile(".*row-0")) if element.text.isdigit()]
    score_team_2 = [(int)(element.text) for element in score_data.find_all(id = re.compile(".*row-1")) if element.text.isdigit()]
    sum_team_1 = sum(score_team_1)
    sum_team_2 = sum(score_team_2)
    status = soup.find(class_ = re.compile('^StatusLayerstyle__GameStateWrapper')).text
    data = re.search("[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}", str(soup.find(class_ = re.compile("^datePickerstyle__InputWrapper")))).group()
    data = datetime.datetime.strptime(data, "%m/%d/%Y").strftime("%a %b %d").upper()
    now = 0

    if (len(score_team_1) != len(score_team_2)):
        now = len(score_team_1)
        score_team_2.append("" if status != "Final" else 'X')
    else: now = -1 * len(score_team_1)

    if(status == "Final"):
        if(len(score_team_1) != len(score_team_2)):
            score_team_2.append("X")
    else:
        for i in range(9 - len(score_team_1)):
            score_team_1.append("")
        for i in range(9 - len(score_team_2)):
            score_team_2.append("")

    score_team_1.append(sum_team_1)
    score_team_2.append(sum_team_2)

    if team == "dodgers":
        color_back = "#004680"
    else:
        color_back = "#862633"
    color_text = "#cccccc"

    df = pd.DataFrame({teams[0]: score_team_1, teams[1]: score_team_2}, index=[i + 1 if i != len(score_team_1) - 1 else "計" for i in range(len(score_team_1))]).T
    fig, ax = plt.subplots(figsize=(5,1))
    fig.patch.set_facecolor(color_back)

    ax.axis("off")
    tb = ax.table(
        cellText=df.values, colLabels=df.columns, rowLabels=teams,
        loc = "center", cellLoc='center'
        )
    tb.scale(1, 1.4)
    for cell in tb.properties()['children']:
        cell.get_text().set_color('white')
        cell.set_edgecolor("white")
        cell.set_facecolor(color_back)

    for i in range(len(score_team_1)):
        tb[0, i].set_color(color_back)
        tb[0, i].set_text_props(color = color_text)
    plt.subplots_adjust(wspace=0.4)
    img_name = str(time.time()).replace('.', '').ljust(17, '0')
    plt.savefig(f"img/{img_name}", facecolor = fig.get_facecolor(), dpi = 500, bbox_inches='tight', pad_inches=0.25)
    organize_files()

    return {"url":f"https://sclas.xyz/img/{img_name}.png", "teams":(f"{teams[0]} VS {teams[1]}"), "data": data, "status": status, "now": (("TOP " if now >= 0 else "BOT ") + f"{abs(now)} " + (teams[0] if now >= 0 else teams[1])), "color": color_back}

def gen_dragons_info():
    load_url = "https://dragons.jp/game/scoreboard/"
    html = requests.get(load_url)
    soup = bs(html.content, "html.parser")
    score_data = soup.find(class_ = "score-board")

    teams = [element.text.strip() for element in score_data.find_all("img", alt = "")]
    score_team_1 = [(int)(element.text) for element in score_data.find_all(href = re.compile("^#0_a"))]
    score_team_2 = [(int)(element.text) for element in score_data.find_all(href = re.compile("^#0_b"))]
    sum_team_1 = sum(score_team_1)
    sum_team_2 = sum(score_team_2)
    status = str(score_data.find(class_ = "state-icon"))
    status = re.search(r'alt=".{1,8}"', status).group().strip("alt=\"")
    data = soup.find(class_ = "date-title-main").text.split()[0]
    now = 0

    if (len(score_team_1) != len(score_team_2)):
        now = len(score_team_1)
        score_team_2.append("" if status != "試合終了" else 'X')
    else: now = -1 * len(score_team_1)

    if(status == "試合終了"):
        if(len(score_team_1) != len(score_team_2)):
            score_team_2.append("X")
    else:
        for i in range(9 - len(score_team_1)):
            score_team_1.append("")
        for i in range(9 - len(score_team_2)):
            score_team_2.append("")

    score_team_1.append(sum_team_1)
    score_team_2.append(sum_team_2)

    color_back = "#222222"
    color_text = "#999999"

    df = pd.DataFrame({teams[0]: score_team_1, teams[1]: score_team_2}, index=[i + 1 if i != len(score_team_1) - 1 else "計" for i in range(len(score_team_1))]).T
    fig, ax = plt.subplots(figsize=(5,1))
    fig.patch.set_facecolor(color_back)

    ax.axis("off")
    tb = ax.table(
        cellText=df.values, colLabels=df.columns, rowLabels=teams, 
        loc = "center", cellLoc='center'
        )
    tb.scale(1, 1.4)
    for cell in tb.properties()['children']:
        cell.get_text().set_color('white')
        cell.set_edgecolor("white")
        cell.set_facecolor(color_back)

    for i in range(len(score_team_1)):
        tb[0, i].set_color(color_back)
        tb[0, i].set_text_props(color = color_text)
    plt.subplots_adjust(wspace=0.4)
    img_name = str(time.time()).replace('.','').ljust(17, '0')
    plt.savefig(f"img/{img_name}", facecolor = fig.get_facecolor(), dpi = 500, bbox_inches='tight', pad_inches=0.25)
    organize_files()

    return {"url": f"https://sclas.xyz/img/{img_name}.png", "teams":(f"{teams[0]} VS {teams[1]}"), "data": data, "status": status, "now": (f"{abs(now)}回" + ("表 " if now >= 0 else "裏 ") + (teams[0] if now >= 0 else teams[1]) + "の攻撃"), "color": color_back}
