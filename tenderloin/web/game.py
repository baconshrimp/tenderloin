"""Websocket logic for actually playing the game."""

import logging

from tenderloin.web import helper

logger = logging.getLogger(__name__)


class TableHandler(helper.TenderloinWebSocketHandler):

    @helper.requires_authentication
    def open(self, tid):
        self.table = self.table_service.get(int(tid))
        logger.info('%s has connected to table %s', self.username, tid)

        self.write_message({
            'type': 'hand',
            'username': self.username,
            'hand': self.table.hands[self.username],
        })
        logger.info('Gave %s their hand of 13 tiles', self.username)
