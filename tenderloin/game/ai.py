class Bot(object):
    """Basic Mahjong AI"""

    def __init__(self, username, send_message):
        self.username = username
        self.send_message = send_message

        # Game state
        self.hand = []
        self.discards = []

    def on_message(self, message):
        """Called when the bot receives a message."""
        if message['type'] == 'draw':
            self.send_message({
                'type': 'discard',
                'tile': message['unicode'],
            })
