"""Tenderloin database common and helpers."""

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


def initialize_db(database_uri='sqlite://'):
    """Initialize the database and return a session context manager.

    Example:
        create_session = initialize_db()
        with create_session() as session:
            session.add(....)
            obj = session.query(Model).get(...)
    """

    engine = create_engine(database_uri, echo=False)
    Base.metadata.create_all(engine)
    SessionMaker = sessionmaker(bind=engine)

    @contextmanager
    def session_context():
        session = SessionMaker()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    return session_context
