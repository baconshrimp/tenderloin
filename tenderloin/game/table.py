import collections
import itertools
import logging
import random
import time

from tenderloin.game.resources import tiles, deck, winds

logger = logging.getLogger(__name__)

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
        self.last_turn_start = 0
        self.turn_time = 30  # seconds

    def add_client(self, username, handler):
        logger.info('Table %s: listener added for %s', self.tid, username)
        self.listeners[username].add(handler)
        self.has_joined_once[username] = True

    def remove_client(self, username, handler):
        logger.info('Table %s: listener removed for %s', self.tid, username)
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

    # Message receiving

    def handle(self, username, message):
        if message['type'] == 'tick':
            return

        logger.info('Table %s: processing %r from %s',
                    self.tid,
                    message,
                    username)

    # Game state

    def can_start(self):
        return not self.has_started and all(self.has_joined_once.values())

    # Game actions

    def tick(self, username):
        if not self.has_started:
            return

        logger.info('Table %s: tick from %s', self.tid, username)

        time_since = time.time() - self.last_turn_start
        turns_since, remainder = divmod(time_since, self.turn_time)
        if turns_since > 0:
            logger.info('Table %s: behind by %s turns', self.tid, turns_since)
            self.last_turn_start = time.time() - remainder

    def start_game(self):
        logger.info('Table %s: starting', self.tid)
        self.has_started = True
        self.game.start()

        # Tell everyone about their hand
        for username in self.listeners:
            self.send_info(username)

        self.last_turn_start = time.time()
