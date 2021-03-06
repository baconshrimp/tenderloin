import collections
import functools
import itertools
import logging
import random

from tornado.ioloop import IOLoop, PeriodicCallback

from tenderloin.game.ai import Bot
from tenderloin.game.resources import (
    deck, winds,
    serialize,
    tile_symbols,
)

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

    def draw_tile(self):
        """Draws a tile for a player."""
        tile = self.deck.popleft()
        self.current_player.hand.append(tile)
        return tile

    def discard_tile(self, tile):
        """Discards a tile from a player's hand."""
        self.current_player.hand.remove(tile)
        self.discards.append((self.current_player.username, tile))

    def start(self):
        """Deals hands and starts the game."""
        for username in self.players:
            self.players[username].hand.extend(
                [self.deck.popleft() for _ in range(13)])

    def next_turn(self):
        """Advances the game state by one turn."""
        username = next(self.turn_order)
        self.current_player = self.players[username]
        return username

    def compute_choices(self, tile):
        """Figures out if any player can make any melds with a tile.

        Yields: username, kong, pong, chows

        """
        possible_chows = [
            [tile.next(1), tile.next(2)],
            [tile.prev(1), tile.next(1)],
            [tile.prev(2), tile.prev(1)],
        ]

        for player in self.players.values():
            if self.current_player == player:
                continue

            # TODO: Make these checks more efficient
            kong = [tile] * 4 if player.hand.count(tile) == 3 else []
            pong = [tile] * 3 if player.hand.count(tile) >= 2 else []
            chows = [sorted(chow + [tile]) for chow in possible_chows
                     if chow[0] in player.hand and chow[1] in player.hand]

            yield player.username, kong, pong, chows


class TableService(object):

    BOT_NAMES = [
        'Jon Snow',
        'Tobias Fünke',
        'Maurice Moss',
    ]

    def __init__(self):
        self.tables = []

    def get(self, tid):
        return self.tables[tid]

    def create(self, usernames):
        bots = self.BOT_NAMES[:4 - len(usernames)]
        table = Table(len(self.tables), usernames + bots)

        for username in bots:
            handle = functools.partial(IOLoop.current().add_callback,
                                       table.handle,
                                       username)
            bot = Bot(username, handle)
            table.add_client(username, bot.on_message)
        self.tables.append(table)

        return table.tid


class Table(object):

    def __init__(self, tid, usernames):
        self.tid = tid
        self.has_started = False
        self.has_joined_once = {username: False for username in usernames}
        self.listeners = {username: set() for username in usernames}

        random.shuffle(usernames)
        self.game = Game(usernames)

        self.turn_time = 10000  # ms
        self.turn_number = 1
        self.turn_timer = PeriodicCallback(self.end_turn, self.turn_time)
        self.pick_time = 5000  # ms
        self.pick_timer = PeriodicCallback(self.end_pick, self.pick_time)

        self.can_discard = False

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
            listener(message)

    def _broadcast_message(self, type_, message):
        """Send a message to all listeners on any username."""
        message.update({'type': type_})
        for listener in itertools.chain(*self.listeners.values()):
            listener(message)

    # Message sending

    def send_info(self, username):
        """Tells a player about their hand and wind."""
        hand = sorted(self.game.players[username].hand)
        self._send_message('info', username, {
            'players': [{
                'username': player.username,
                'wind': player.wind,
            } for player in self.game.players.values()],
            'hand': serialize(hand),
            'unicode': [tile.symbol for tile in hand],
            'turn_time': self.turn_time,
        })

    def send_pick_choices(self):
        tile = self.game.discards[-1][1]
        for username, kong, pong, chows in self.game.compute_choices(tile):
            self._send_message('pick_choices', username, {
                'tile': tile.code,
                'unicode': tile.symbol,
                'kong': serialize(kong),
                'pong': serialize(pong),
                'chows': [serialize(chow) for chow in chows],
            })

    def broadcast_info(self):
        for username in self.listeners:
            self.send_info(username)

    def broadcast_pick_start(self):
        self._broadcast_message('start_pick', {
            'number': self.turn_number,
            'pick_time': self.pick_time,
        })

    def broadcast_pick_end(self):
        self._broadcast_message('end_pick', {
            'number': self.turn_number,
        })

    def broadcast_turn_start(self, username):
        self._broadcast_message('start_turn', {
            'username': username,
            'number': self.turn_number,
            'turn_time': self.turn_time,
        })

    def broadcast_turn_end(self, username):
        self._broadcast_message('end_turn', {
            'username': username,
            'number': self.turn_number,
        })

    def broadcast_draw(self, username, tile):
        self._send_message('draw', username, {
            'tile': tile.code,
            'unicode': tile.symbol,
        })

    def broadcast_discard(self, username, tile):
        self._broadcast_message('discard', {
            'username': username,
            'tile': tile.code,
            'unicode': tile.symbol,
        })

    # Message receiving

    def handle(self, username, message):
        if self.game.current_player.username == username:
            logger.info('Table %s: processing %r from %s',
                        self.tid,
                        message,
                        username)
            if message['type'] == 'discard' and self.can_discard:
                self.handle_discard(username, message)
        else:
            logger.info('Table %s: ignoring message from %s',
                        self.tid,
                        username)

    def handle_discard(self, username, message):
        # XXX: Eventually David will send me the ascii-code for the tile
        tile = tile_symbols[message['tile']]

        try:
            self.game.discard_tile(tile)
        except ValueError:
            return

        self.broadcast_discard(username, tile)
        self.end_turn(force_discard=False)

    # Game state

    def can_start(self):
        return not self.has_started and all(self.has_joined_once.values())

    # Game actions

    def start_game(self):
        logger.info('Table %s: starting game', self.tid)
        self.has_started = True
        self.game.start()

        self.broadcast_info()
        self.start_turn()

    def start_pick(self):
        """Start the pick phase."""
        self.turn_number += 1
        logger.info('Table %s: starting pick %s',
                    self.tid,
                    self.turn_number)
        self.broadcast_pick_start()
        self.send_pick_choices()
        self.pick_timer.start()

    def end_pick(self):
        """End the pick phase."""
        self.pick_timer.stop()
        logger.info('Table %s: ending pick %s',
                    self.tid,
                    self.turn_number)
        self.broadcast_pick_end()
        self.start_turn()

    def start_turn(self, draw=True):
        """Start the next player's turn."""
        username = self.game.next_turn()

        logger.info('Table %s: starting turn %s, %s',
                    self.tid,
                    self.turn_number,
                    username)
        self.broadcast_turn_start(username)

        if draw:
            tile = self.game.draw_tile()
            self.broadcast_draw(username, tile)

        self.can_discard = True
        self.turn_timer.start()

    def end_turn(self, force_discard=True):
        """Ends the current player's turn."""
        self.turn_timer.stop()
        self.can_discard = False

        if force_discard:
            current = self.game.current_player
            tile = current.hand[-1]
            self.game.discard_tile(tile)
            self.broadcast_discard(current.username, tile)

        self.broadcast_turn_end(self.game.current_player.username)
        if self.game.deck:
            self.start_pick()
        else:
            logger.info('Table %s: deck depleted, timers stopped', self.tid)
