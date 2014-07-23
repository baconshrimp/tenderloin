import collections
import itertools
import logging
import random

from tornado.ioloop import PeriodicCallback

from tenderloin.game.resources import tiles, reverse_tiles, deck, winds

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
        self.discards = []  # [(username, tile)]

        self.players = self._create_players(usernames)
        random.shuffle(self.deck)
        self.turn_order = itertools.cycle(usernames)

        self.current_player = None

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
        self.players[username].hand.append(tile)
        return tile

    def discard_tile(self, username, tile):
        """Discards a tile from a player's hand."""
        self.players[username].hand.remove(tile)
        self.discards.append((username, tile))

    def start(self):
        """Deals hands and starts the game."""
        for username in self.players:
            self.players[username].hand.extend(
                [self.deck.popleft() for _ in range(13)])

    def next_turn(self):
        """Advances the game state by one turn."""
        username = next(self.turn_order)
        tile = self.draw_tile(username)
        self.current_player = username
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
        self.turn_time = 10000  # ms

        self.turn_number = 0
        self.turn_timer = PeriodicCallback(self.next_turn, self.turn_time)

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
            'turn_time': self.turn_time,
        })

    def broadcast_info(self):
        for username in self.listeners:
            self.send_info(username)

    def broadcast_turn_start(self, username, tile):
        self._broadcast_message('turn_start', {
            'username': username,
            'number': self.turn_number,
        })
        self._send_message('draw', username, {
            'tile': tile,
            'unicode': tiles[tile],
        })

    def broadcast_turn_end(self, username):
        self._broadcast_message('turn_end', {
            'username': username,
            'number': self.turn_number,
        })

    def broadcast_discard(self, username, tile):
        self._broadcast_message('discard', {
            'username': username,
            'tile': tile,
            'unicode': tiles[tile],
        })

    # Message receiving

    def handle(self, username, message):
        if self.game.current_player == username:
            logger.info('Table %s: processing %r from %s',
                        self.tid,
                        message,
                        username)
            if message['type'] == 'discard':
                self.handle_discard(username, message)
        else:
            logger.info('Table %s: ignoring message from %s',
                        self.tid,
                        username)

    def handle_discard(self, username, message):
        # XXX: Eventually David will send me the ascii-code for the tile
        tile = reverse_tiles[message['tile']]

        try:
            self.game.discard_tile(username, tile)
        except ValueError:
            return

        self.broadcast_discard(username, tile)
        self.next_turn()

    # Game state

    def can_start(self):
        return not self.has_started and all(self.has_joined_once.values())

    # Game actions

    def start_game(self):
        logger.info('Table %s: starting', self.tid)
        self.has_started = True
        self.game.start()

        self.broadcast_info()
        self.next_turn()

    def next_turn(self):
        self.turn_timer.stop()
        self.turn_number += 1
        if len(self.game.deck):
            logger.info('Table %s: starting turn %s',
                        self.tid,
                        self.turn_number)
            username, tile = self.game.next_turn()
            self.broadcast_turn_start(username, tile)
            self.turn_timer.start()
        else:
            logger.info('Table %s: deck depleted', self.tid)
