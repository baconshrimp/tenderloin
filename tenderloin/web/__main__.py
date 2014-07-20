"""Kind of hacky server for the API and client code."""

import logging
import os

from tornado.options import define, options
import tornado.ioloop
import tornado.web

from tenderloin.db import initialize_db, User
from tenderloin.web import auth, chat, game

BASE_PATH = os.path.dirname(os.path.dirname(__file__))

define("port", default=8000, help="run on the given port", type=int)


class SingleFileHandler(tornado.web.StaticFileHandler):
    """FileHandler that only reads a single static file."""

    @classmethod
    def get_absolute_path(cls, root, path):
        return tornado.web.StaticFileHandler.get_absolute_path(root,
                                                               "index.html")


def get_application():
    static_path = os.path.join(BASE_PATH, 'client', 'static')
    static_config = {'path': static_path}

    api_config = {'create_session': initialize_db()}
    app_config = {'cookie_secret': 'changeme'}

    # TODO: Add a flag to create these example users
    with api_config['create_session']() as session:
        session.add(User('michael', 'michael'))
        session.add(User('david', 'david'))
        session.add(User('tom', 'tom'))
        session.add(User('allen', 'allen'))

    application = tornado.web.Application([
        # HTTP API
        (r'/api/login', auth.LoginHandler, api_config),

        # Chat API
        (r'/api/chat', chat.ChatHandler),

        # Game API
        (r'/api/table/(?P<tid>\d+)', game.TableHandler),

        (r'/(.*\..*)', tornado.web.StaticFileHandler, static_config),
        (r'/(.*)', SingleFileHandler, static_config),
    ], **app_config)
    return application


def main():
    logging.basicConfig(format='[%(levelname)s][%(name)s]: %(message)s')
    logging.getLogger().setLevel(logging.DEBUG)

    tornado.options.parse_command_line()
    application = get_application()
    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
