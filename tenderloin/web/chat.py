"""Real time chat websocket service."""

import logging

from tornado.escape import json_decode
import tornado.websocket

logger = logging.getLogger(__name__)


class ChatHandler(tornado.websocket.WebSocketHandler):

    def on_message(self, message):
        data = json_decode(message)
        logger.debug('Recieved: %r', data)
        new_data = {
            'name': data['name'][::-1].lower().title(),
            'message': data['message'][::-1],
        }
        logger.debug('Sending: %r', new_data)

        self.write_message(new_data)
