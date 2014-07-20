import collections
import random


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

        # Create the deck
        self.deck = collections.deque(
            ['character-{}'.format(i) for i in range(1, 10)] * 4
            + ['circle-{}'.format(i) for i in range(1, 10)] * 4
            + ['bamboo-{}'.format(i) for i in range(1, 10)] * 4
            + ['dragon-red', 'dragon-green', 'dragon-white'] * 4
            + ['wind-north', 'wind-east', 'wind-south', 'wind--west'] * 4
            + ['flower-1', 'flower-2', 'flower-3', 'flower-4'] * 2
        )
        random.shuffle(self.deck)

        # Setup the players
        self.players = collections.OrderedDict()
        self.has_joined_once = {}
        for username in usernames:
            self.players[username] = {
                'hand': [],
                'flowers': [],
                'wind': None,
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

    def broadcast_message(self, type_, message):
        message.update({'type': type_})
        for username in self.players:
            for handler in self.players[username]['listeners']:
                handler.write_message(message)

    def can_start(self):
        return not self.has_started or all(self.has_joined_once.values())

    def start_game(self):
        self.has_started = True

        # Deal tiles
        for username in self.players:
            self.players[username]['hand'] = \
                [self.deck.popleft() for _ in range(13)]
            self.send_message('hand', username, {
                'hand': self.players[username]['hand'],
            })
