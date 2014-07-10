"""Real time chat websocket service."""

import logging

from tenderloin.web import helper

logger = logging.getLogger(__name__)


class Chatroom(object):

    def __init__(self):
        self.clients = set()

    def broadcast(self, message):
        for client in self.clients:
            client.write_message(message)

    def send_join(self, username):
        self.broadcast({
            'type': 'join',
            'username': username,
        })

    def send_part(self, username):
        self.broadcast({
            'type': 'part',
            'username': username,
        })

    def send_regular(self, username, message):
        self.broadcast({
            'type': 'regular',
            'username': username,
            'message': message,
        })


class ChatHandler(helper.TenderloinWebSocketHandler):

    MESSAGE_SCHEMA = {
        'type': 'object',
        'properties': {
            'message': {'type': 'string'},
        },
        'required': ['message'],
    }

    chatroom = Chatroom()

    def initialize(self):
        self.username = self.get_current_username()

    @helper.requires_authentication
    def open(self):
        self.chatroom.clients.add(self)
        self.chatroom.send_join(self.username)

    def on_close(self):
        self.chatroom.clients.remove(self)
        self.chatroom.send_part(self.username)

    def on_message(self, message):
        data = helper.parse_json_or_fail(message, self.MESSAGE_SCHEMA)
        self.chatroom.send_regular(self.username, data['message'])
