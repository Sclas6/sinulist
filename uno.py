import numpy as np
from uno_constant import *

class Card():
    def __init__(self, color: int, number: int):
        self.color = color
        self.number = number

    def __str__(self):
        return f"{COLORS[self.color]}, {NUMBERS[self.number]}"

class Uno_User():
    def __init__(self, id, hand):
        self.id = id
        self.hand = hand

    def pop_card(self, color, num):
        for i, card in enumerate(self.hand):
            if card.color == color and card.number == num:
                self.hand = np.delete(self.hand, i)
                return card
        return None
    
    def serach_card(self, color, num):
        for card in self.hand:
            if card.color == color and card.number == num:
                return True
        return False

    def draw_card(self, card: Card):
        self.hand = np.append(self.hand, card)

class Uno_Game():
    def __init__(self, id):
        self.id = id
        self.deck = create_deck()
        self.turn = 0
        self.reverse = 1
        self.next_user = None
        self.debt = 0
        self.status = None
        self.users_raw = [] # list of str
        self.users = [] # list of Ofject
        self.trush = []
        self.prev_trush = []
        self.ranking = []

    def start(self):
        self.status = "START"
        self.next_user = self.users_raw[0]
        for user_str in self.users_raw:
            user = Uno_User(user_str, self.deck[:7])
            self.deck = np.delete(self.deck, np.s_[:7])
            self.users.append(user)
        while True:
            card: Card = self.deck[0]
            self.deck = np.delete(self.deck, 0)
            self.trush.append(card)
            if card.color != ACTION and card.number < 10: break

    def search_user(self, id) -> Uno_User:
        for user in self.users:
            if user.id == id:
                return user

    def rm_user(self, id):
        for i, user in enumerate(self.users_raw):
            if user == id:
                del self.users_raw[i]
                self.ranking.append(user)

    def can_pop(self, color: int, num: int) -> bool:
        top: Card = self.trush[-1]
        #print(f"trush: {top} your: {COLORS[color]} {NUMBERS[num]}")
        if self.debt != 0:
            if top.number == DRAW2:
                if top.number == num: return True
                else: return False
            if top.number == DRAW4:
                if top.number == num: return True
                else: return False
        if top.color == color or top.number == num or color == ACTION: return True
        if num == WILD or num == DRAW4: return True
        else: return False

    def can_multiple_pop(self, color: int, num: int) -> bool:
        top: Card = self.trush[-1]
        if top.number == num and color != ACTION: return True
        else: return False

    def next(self):
        self.turn += self.reverse
        i = self.turn % len(self.users_raw)
        self.next_user = self.users_raw[i]
        return self.users_raw[i]


def create_deck():
    cards = np.array([])
    for color in range(len(COLORS)):
        if color != ACTION:
            for num in range(0, 13):
                card = Card(color, num)
                cards = np.append(cards, card)
                if num != 0: cards = np.append(cards, card)
        else:
            for num in range(13, 15):
                card = Card(color, num)
                for _ in range(4): cards = np.append(cards, card)
    np.random.shuffle(cards)
    return cards