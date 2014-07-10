import tornado.web

from tenderloin.db import User
from tenderloin.web import helper


class LoginHandler(helper.TenderloinRequestHandler):

    POST_SCHEMA = {
        'type': 'object',
        'properties': {
            'username': {'type': 'string'},
            'password': {'type': 'string'},
        },
        'required': ['username', 'password'],
    }

    def get(self):
        """Returns the user's username if they are logged in.

        Args: None

        Returns:
            {
                'username': ...,
            }

        """
        username = self.get_current_username()
        self.write({'username': username})

    def post(self):
        """Logs a user in.

        Args:
            {
                'username': ...,
                'password': ...,
            }

        Returns: None

        """
        body = self.parse_body_or_fail(self.POST_SCHEMA)

        with self.create_session() as session:
            user = session.query(User).get(body['username'])

            if user is None or not user.is_valid(body['password']):
                raise tornado.web.HTTPError(400)

        self.set_secure_cookie('username', body['username'])

    @helper.requires_authentication
    def delete(self):
        """Logs out a user."""
        self.clear_cookie('username')
