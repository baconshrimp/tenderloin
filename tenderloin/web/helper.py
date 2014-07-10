import functools

from tornado import httputil
import jsonschema
import jsonschema.exceptions
import tornado.escape
import tornado.web
import tornado.websocket


def requires_authentication(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        username = self.get_secure_cookie('username')
        if username:
            return func(self, *args, **kwargs)
        else:
            if isinstance(self, TenderloinWebSocketHandler):
                self.write_error('auth required')
                self.close()
            else:
                raise tornado.web.HTTPError(401)

    return wrapper


def parse_json_or_fail(message, schema):
    """Parses a message as json and validates it against a schema."""
    try:
        body = tornado.escape.json_decode(message)
    except ValueError as e:
        raise tornado.web.HTTPError(400, reason=str(e))

    try:
        jsonschema.validate(body, schema)
    except jsonschema.exceptions.ValidationError as e:
        raise tornado.web.HTTPError(400, reason=e.message)

    return body


class TenderloinRequestHandler(tornado.web.RequestHandler):

    def initialize(self, create_session):
        self.create_session = create_session

    def write_error(self, status_code, **kwargs):
        error = kwargs['exc_info'][1]
        reason = error.reason or httputil.responses.get(error.status_code)
        self.write({'reason': reason})

    # Useful stuff

    def parse_body_or_fail(self, schema):
        """Parses the request body according to a json schema."""
        return parse_json_or_fail(self.request.body.decode('utf-8'), schema)

    def get_current_username(self):
        """Returns the current logged in user's username."""
        username = self.get_secure_cookie('username')
        if username is None:
            return None
        else:
            return username.decode('utf-8')


class TenderloinWebSocketHandler(tornado.websocket.WebSocketHandler):

    def write_error(self, reason):
        """Sends an error message to the client."""
        self.write_message({
            'status': 'error',
            'reason': reason,
        })

    def get_current_username(self):
        """Returns the current logged in user's username."""
        username = self.get_secure_cookie('username')
        if username is None:
            return None
        else:
            return username.decode('utf-8')
