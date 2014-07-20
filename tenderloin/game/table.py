import collections
import random

from tenderloin.game.resources import tiles, deck, winds


class TableService(object):

    def __init__(self):
        self.tables = []

    def get(self, tid):
        return self.tables[tid]

    def create(self, usernames):
        tid = len(self.tables)
        self.tables.append(Table(tid, usernames))
        return tid


class Table(object):

    def __init__(self, tid, usernames):
        # Some housekeeping
        self.has_started = False
        self.tid = tid
        random.shuffle(usernames)

        # Create the deck
        self.deck = collections.deque(deck)
        random.shuffle(self.deck)

        # Setup the players
        self.players = collections.OrderedDict()
        self.has_joined_once = {}
        for username, wind in zip(usernames, winds):
            self.players[username] = {
                'hand': [],
                'flowers': [],
                'wind': wind,
                'listeners': set(),
            }
            self.has_joined_once[username] = False

    def add_client(self, username, handler):
        self.players[username]['listeners'].add(handler)
        self.has_joined_once[username] = True

    def remove_client(self, username, handler):
        self.players[username]['listeners'].remove(handler)

    def send_message(self, type_, username, message):
        message.update({
            'type': type_,
            'username': username,
        })
        for handler in self.players[username]['listeners']:
            handler.write_message(message)

    def send_info(self, username):
        hand = sorted(self.players[username]['hand'], key=tiles.get)
        wind = self.players[username]['wind']

        self.send_message('info', username, {
            'players': [{
                'username': player,
                'wind': info['wind'],
            } for player, info in self.players.items()],
            'wind': wind,
            'hand': hand,
            'unicode': [tiles[tile] for tile in hand],
        })

    def draw_tile(self, username):
        tile = self.deck.popleft()
        self.players[username]['hand'].append(tile)
        self.send_message('draw', username, {
            'tile': tile,
            'unicode': tiles[tile],
        })

    def broadcast_message(self, type_, message):
        message.update({'type': type_})
        for username in self.players:
            for handler in self.players[username]['listeners']:
                handler.write_message(message)

    def can_start(self):
        return not self.has_started and all(self.has_joined_once.values())

    def start_game(self):
        self.has_started = True

        # Deal tiles
        for username in self.players:
            self.players[username]['hand'] = \
                [self.deck.popleft() for _ in range(13)]
            self.send_info(username)
