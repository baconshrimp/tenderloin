"""Websocket logic for actually playing the game."""

import collections
import logging

from tenderloin.web import helper

logger = logging.getLogger(__name__)


class TableHandler(helper.TenderloinWebSocketHandler):

    tables = collections.defaultdict(set)

    def initialize(self):
        self.username = self.get_current_username()

    @helper.requires_authentication
    def open(self, tid):
        self.table_id = tid
        self.tables[tid].add(self)

        logging.info('User %s has entered table %s', self.username, tid)
        self.write_message({
            'players': [client.username for client in self.tables[tid]],
        })

    def on_close(self):
        self.tables[self.table_id].remove(self)
