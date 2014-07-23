"""Websocket logic for actually playing the game."""

import logging

from tenderloin.web import helper

logger = logging.getLogger(__name__)


class TableHandler(helper.TenderloinWebSocketHandler):

    GENERAL_SCHEMA = {
        'type': 'object',
        'properties': {
            'type': {'type': 'string'},
        },
        'required': ['type'],
    }

    @helper.requires_authentication
    def open(self, tid):
        self.table = self.table_service.get(int(tid))
        self.table.add_client(self.username, self)

        if self.table.can_start():
            self.table.start_game()

    def on_message(self, raw_message):
        message = helper.parse_json_or_fail(raw_message, self.GENERAL_SCHEMA)
        self.table.handle(self.username, message)

    def on_close(self):
        self.table.remove_client(self.username, self)
