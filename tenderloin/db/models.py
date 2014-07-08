"""Tenderloin database models."""

from sqlalchemy import Column, String
import pbkdf2

from .core import Base


class User(Base):
    """Represents a user."""

    __tablename__ = 'users'

    username = Column(String(32), primary_key=True, nullable=False)
    password_hash = Column(String(100), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def __eq__(self, other):
        return self.username == other.username

    def set_password(self, password):
        """Sets the password for the user."""
        self.password_hash = pbkdf2.crypt(password)

    def is_valid(self, password):
        """Returns true if the password is correct for this user."""
        return self.password_hash == pbkdf2.crypt(password, self.password_hash)
