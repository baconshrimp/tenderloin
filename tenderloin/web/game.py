"""Websocket logic for actually playing the game."""

import logging

from tenderloin.web import helper

logger = logging.getLogger(__name__)


class TableHandler(helper.TenderloinWebSocketHandler):

    @helper.requires_authentication
    def open(self, tid):
        self.table = self.table_service.get(int(tid))
        self.table.add_client(self.username, self)
        logger.info('%s has connected to table %s', self.username, tid)

        if self.table.can_start():
            logger.info('%s is starting table %s', self.username, tid)
            self.table.start_game()

            # Make everyone draw once
            for username in self.table.players:
                self.table.draw_tile(username)

    def on_message(self, message):
        logger.info('Got message from %s: %s', self.username, message)

    def on_close(self):
        self.table.remove_client(self.username, self)
        logger.info('%s has disconnected from table %s',
                    self.username,
                    self.table.tid)
