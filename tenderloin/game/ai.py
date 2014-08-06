import functools


class Bot(object):
    """Basic Mahjong AI"""

    def __init__(self, username, send_message):
        self.username = username
        self.send_message = functools.partial(send_message, username)

        # Game state
        self.hand = []
        self.discards = []

    def on_message(self, message):
        """Called when the bot receives a message."""
        if message['type'] == 'info':
            self.hand = message['hand']
        elif message['type'] == 'discard':
            self.discards.append(message['tile'])
