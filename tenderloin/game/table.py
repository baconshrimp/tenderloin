import collections
import itertools
import random

from tenderloin.game.resources import tiles, deck, winds


Player = collections.namedtuple('Player', [
    'username',
    'hand',
    'flowers',
    'wind',
])


class Game(object):

    def __init__(self, usernames):
        self.deck = collections.deque(deck)
        self.players = self._create_players(usernames)
        random.shuffle(self.deck)
        self.turn_order = itertools.cycle(usernames)

    def _create_players(self, usernames):
        players = {}
        for username, wind in zip(usernames, winds):
            players[username] = Player(
                username=username,
                hand=[],
                flowers=[],
                wind=wind,
            )
        return players

    def draw_tile(self, username):
        """Draws a tile for a player."""
        tile = self.deck.popleft()
        self.players[username].append(tile)
        return tile

    def start(self):
        """Deals hands and starts the game."""
        for username in self.players:
            self.players[username].hand.extend(
                [self.deck.popleft() for _ in range(13)])

    def next_turn(self):
        """Advances the game state by one turn."""
        username = next(self.turn_order)
        tile = self.draw_tile(username)
        return username, tile


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
        self.tid = tid
        self.has_started = False
        self.has_joined_once = {username: False for username in usernames}
        self.listeners = {username: set() for username in usernames}

        random.shuffle(usernames)
        self.game = Game(usernames)

    def add_client(self, username, handler):
        self.listeners[username].add(handler)
        self.has_joined_once[username] = True

    def remove_client(self, username, handler):
        self.listeners[username].remove(handler)

    def _send_message(self, type_, username, message):
        """Send a message to all listeners on a username."""
        message.update({
            'type': type_,
            'username': username,
        })
        for listener in self.listeners[username]:
            listener.write_message(message)

    def _broadcast_message(self, type_, message):
        """Send a message to all listeners on any username."""
        message.update({'type': type_})
        for listener in itertools.chain(*self.listeners.values()):
            listener.write_message(message)

    # Message sending

    def send_info(self, username):
        """Tells a player about their hand and wind."""
        hand = sorted(self.game.players[username].hand, key=tiles.get)
        self._send_message('info', username, {
            'players': [{
                'username': player.username,
                'wind': player.wind,
            } for player in self.game.players.values()],
            'hand': hand,
            'unicode': [tiles[tile] for tile in hand],
        })

    # Game state

    def can_start(self):
        return not self.has_started and all(self.has_joined_once.values())

    # Game actions

    def start_game(self):
        self.has_started = True
        self.game.start()

        # Tell everyone about their hand
        for username in self.listeners:
            self.send_info(username)
