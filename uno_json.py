from uno_constant import *
from uno import *


def gen_start_json():
    contents = {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": "https://pbs.twimg.com/profile_images/848189031779192832/zEZWpPOL_400x400.jpg",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover",
            "action": {
                "type": "uri",
                "uri": "http://linecorp.com/"
            }
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "UNO",
                    "weight": "bold",
                    "size": "xl"
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "参加",
                        "text": "uno_join"
                    }
                },
                {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "text": "uno_check_participant",
                        "label": "参加確認"
                    },
                    "style": "secondary",
                    "height": "sm"
                }
            ],
            "flex": 0
        }
    }
    return contents


def uno_check_participant(users: list):
    contents = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "UNO",
                    "size": "xl"
                },
                {
                    "type": "separator",
                    "color": "#FFFFFF00",
                    "margin": "xxl"
                },
                {
                    "type": "text",
                    "text": "参加者",
                    "size": "sm",
                    "color": "#aaaaaa"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            ]
        }
    }
    for user in users:
        contents["body"]["contents"][3]["contents"].append(
            {
                "type": "text",
                "text": f"{user}"
            }
        )
    if len(users) > 1:
        contents["footer"]["contents"].append(
            {
                "type": "button",
                "action": {
                    "type": "message",
                    "label": "ゲーム開始",
                    "text": "uno_start_game"
                },
                "style": "primary"
            }
        )
    else:
        contents["footer"]["contents"].append(
            {
                "type": "text",
                "text": "2人以上の参加者が必要です",
                "align": "center"
            }
        )
    return contents

def get_color_code(color):
        color_code = None
        if color == YELLOW:
            color_code = "#FFDC16"
        elif color == BLUE:
            color_code = "#0B69B1"
        elif color == RED:
            color_code = "#DC1917"
        elif color == GREEN:
            color_code = "#549F20"
        else:
            color_code = "#000000"
        return color_code


def gen_hand_json(hand: list, game, mode = 0):
    contents = {
        "type": "carousel",
        "contents": [
            {
                "type": "bubble",
                "hero": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "image",
                            "url": f"https://sclas.xyz/img/{game.trush[-1].number}.png",
                            "aspectMode": "cover",
                            "backgroundColor": get_color_code(game.trush[-1].color),
                            "aspectRatio": "75:48",
                            "size": "full"
                        }
                    ]
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "UNO",
                            "size": "xl"
                        },
                        {
                            "type": "separator",
                            "margin": "xxl",
                            "color": "#FFFFFF00"
                        },
                        {
                            "type": "text",
                            "text": "捨てるカードを選択してください！\n複数枚を捨てる場合は、一番下にするカードを選択してください。",
                            "wrap": True
                        }
                    ]
                }
            }
        ]
    }
    if mode != 0:
        contents["contents"][0]["body"]["contents"].append(
            {
                "type": "button",
                "action": {
                    "type": "message",
                    "label": "選択終了",
                    "text": f"{game.id}_uno_end_select"
                }
            }
        )
    for i, card in enumerate(hand, 1):
        if mode == 0:
            can_pop = game.can_pop(card.color, card.number)
        else:
            can_pop = game.can_multiple_pop(card.color, card.number)
        if len(hand) == 1 and card.number >= 10: can_pop = False
        if i % 2 == 1:
            contents["contents"].append(
                {
                    "type": "bubble",
                    "hero": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "image",
                                "url": f"https://sclas.xyz/img/{card.number}.png",
                                "aspectMode": "cover",
                                "aspectRatio": "75:48",
                                "size": "full",
                                "backgroundColor": get_color_code(card.color)
                            },
                            {
                                "type": "separator",
                                "margin": "md",
                                "color": "#FFFFFF00"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "separator",
                                        "margin": "md",
                                        "color": "#FFFFFF00"
                                    }
                                ]
                            }
                        ]
                    },
                    "footer": {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        ]
                    }
                }
            )
            if can_pop:
                contents["contents"][int((i - 1) / 2) + 1]["hero"]["contents"][2]["contents"].append(
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "選択",
                            "text": f"{game.id}_uno_pop_{card.color}_{card.number}" if mode == 0 else f"{game.id}_uno_multiple_pop_{card.color}_{card.number}"
                        },
                        "style": "primary"
                    }
                )
                if card.color != ACTION and mode == 0:
                    contents["contents"][int((i - 1) / 2) + 1]["hero"]["contents"][2]["contents"].append(
                        {
                            "type": "separator",
                            "margin": "md",
                                    "color": "#FFFFFF00"
                        }
                    )
                    contents["contents"][int((i - 1) / 2) + 1]["hero"]["contents"][2]["contents"].append(
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                        "label": "複数選択",
                                        "text": f"{game.id}_uno_multiple_pop_{card.color}_{card.number}"
                            },
                            "style": "primary"
                        }
                    )
            else:
                contents["contents"][int((i - 1) / 2) + 1]["hero"]["contents"][2]["contents"].append(
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": "捨てられません",
                            "data": "none"
                        },
                        "style": "secondary"
                    }
                )
            contents["contents"][int((i - 1) / 2) + 1]["hero"]["contents"][2]["contents"].append(
                {
                    "type": "separator",
                    "margin": "md",
                    "color": "#FFFFFF00"
                }
            )
        else:
            contents["contents"][int((i - 1) / 2) + 1]["hero"]["contents"].append(
                {
                    "type": "image",
                    "url": f"https://sclas.xyz/img/{card.number}.png",
                    "aspectMode": "cover",
                    "aspectRatio": "75:48",
                    "size": "full",
                    "backgroundColor": get_color_code(card.color)
                }
            )
            if can_pop:
                contents["contents"][int((i - 1) / 2) + 1]["footer"]["contents"].append(
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "選択",
                            "text": f"{game.id}_uno_pop_{card.color}_{card.number}" if mode == 0 else f"{game.id}_uno_multiple_pop_{card.color}_{card.number}"
                        },
                        "style": "primary"
                    }
                )
                if card.color != ACTION and mode == 0:
                    contents["contents"][int((i - 1) / 2) + 1]["footer"]["contents"].append(
                        {
                            "type": "separator",
                            "margin": "md",
                                    "color": "#FFFFFF00"
                        }
                    )
                    contents["contents"][int((i - 1) / 2) + 1]["footer"]["contents"].append(
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                        "label": "複数選択",
                                        "text": f"{game.id}_uno_multiple_pop_{card.color}_{card.number}"
                            },
                            "style": "primary"
                        }
                    )
            else:
                contents["contents"][int((i - 1) / 2) + 1]["footer"]["contents"].append(
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": "捨てられません",
                            "data": "none"
                        },
                        "style": "secondary"
                    }
                )

    if mode == 0:
        contents["contents"].append(
            {
                "type": "bubble",
                "hero": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "image",
                            "aspectMode": "cover",
                            "backgroundColor": "#FF0000",
                            "aspectRatio": "75:48",
                            "size": "full",
                            "url": "https://pbs.twimg.com/profile_images/848189031779192832/zEZWpPOL_400x400.jpg"
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "カードを引く" if game.debt == 0 else f"カードを引く ({game.debt}枚)",
                                "text": f"{game.id}_uno_draw_1" if game.debt == 0 else f"{game.id}_uno_draw_{game.debt}"
                            },
                            "style": "secondary"
                        }
                    ]
                }
            }
        )
    return contents

def gen_deck_info_json(current, next, game: Uno_Game, message: list):
    contents = {
    "type": "bubble",
    "hero": {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "image",
                "url": f"https://sclas.xyz/img/{game.trush[-1].number}.png",
                "aspectMode": "cover",
                "backgroundColor": get_color_code(game.trush[-1].color),
                "aspectRatio": "75:48",
                "size": "full"
            },
            {
                "type": "text",
                "text": "山札",
                "position": "relative",
                "align": "center",
                "size": "lg",
                "weight": "bold"
            }
        ]
    },
    "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
        ]
    }
}
    if current != None:
        for card in game.prev_trush:
            contents["body"]["contents"].append(
                {
                    "type": "text",
                    "text": f"{current}さんが{COLORS[card.color]}の{NUMBERS[card.number]}を捨てました！",
                    "wrap": True
                }
            )
    for str in message:
        contents["body"]["contents"].append(
            {
                "type": "text",
                "text": f"{str}",
                "wrap": True
            }
        )
    contents["body"]["contents"].append(
        {
            "type": "text",
            "text": f"次は{next}さんのターンです",
            "wrap": True
        }
    )
    return contents

def gen_choice_color_json(num: int, game):
    contents = {
    "type": "bubble",
    "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": "色選択",
                "size": "xl"
            }
        ]
    },
    "footer": {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "黄色",
                            "text": f"{game.id}_uno_pop_0_{num}"
                        },
                        "style": "primary"
                    },
                    {
                        "type": "separator",
                        "margin": "md",
                        "color": "#FFFFFF00"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "青色",
                            "text": f"{game.id}_uno_pop_1_{num}"
                        },
                        "style": "primary"
                    }
                ]
            },
            {
                "type": "separator",
                "margin": "md",
                "color": "#FFFFFF00"
            },
            {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "赤色",
                            "text": f"{game.id}_uno_pop_2_{num}"
                        },
                        "style": "primary"
                    },
                    {
                        "type": "separator",
                        "margin": "md",
                        "color": "#FFFFFF00"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "緑色",
                            "text": f"{game.id}_uno_pop_3_{num}"
                        },
                        "style": "primary"
                    }
                ]
            }
        ]
    }
}
    return contents

def gen_result_json(users: list):
    contents = {
    "type": "bubble",
    "hero": {
        "type": "image",
        "url": "https://pbs.twimg.com/profile_images/848189031779192832/zEZWpPOL_400x400.jpg",
        "aspectMode": "cover",
        "size": "full",
        "aspectRatio": "75:48"
    },
    "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": "リザルト",
                "size": "sm"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [

                ]
            }
        ]
    }
}
    for i, user in enumerate(users, 1):
        contents["body"]["contents"][1]["contents"].append(
            {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"{i}位 ",
                                "size": "xl" if i == 1 else "xxs",
                                "flex": 1
                            }
                        ],
                        "width": "60px"
                    },
                    {
                        "type": "text",
                        "text": f"{user}",
                        "size": "xl" if i == 1 else "xxs"
                    }
                ],
                "alignItems": "center"
            }
        )
    return contents