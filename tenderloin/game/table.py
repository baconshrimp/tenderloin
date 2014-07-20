import collections
import random


class TableService(object):

    def __init__(self):
        self.tables = []

    def get(self, tid):
        return self.tables[tid]

    def create(self, usernames):
        self.tables.append(Table(usernames))
        return len(self.tables) - 1


class Table(object):

    def __init__(self, usernames):
        self.deck = collections.deque(
            ['Character:{}'.format(i) for i in range(1, 10)] * 4
            + ['Circle:{}'.format(i) for i in range(1, 10)] * 4
            + ['Bamboo:{}'.format(i) for i in range(1, 10)] * 4
            + ['Dragon:Red', 'Dragon:Green', 'Dragon:White'] * 4
            + ['Wind:North', 'Wind:East', 'Wind:South', 'Wind:West'] * 4
            + ['Flower:1', 'Flower:2', 'Flower:3', 'Flower:4'] * 2
        )
        random.shuffle(self.deck)
        self.hands = self.deal_hands(usernames)

    def deal_hands(self, usernames):
        hands = {}
        for username in usernames:
            hands[username] = [self.deck.popleft() for _ in range(13)]
        return hands
