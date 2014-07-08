"""Kind of hacky server for the API and client code."""

import logging
import os

from tornado.options import define, options
import tornado.ioloop
import tornado.web

from tenderloin.web.chat import ChatHandler

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

    application = tornado.web.Application([
        (r"/api/chat", ChatHandler),
        (r"/(.*\..*)", tornado.web.StaticFileHandler, static_config),
        (r"/(.*)", SingleFileHandler, static_config),
    ])
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
