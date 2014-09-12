from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import logging
import uuid
import functools
from contextlib import contextmanager

class Database(object):
    def __init__(self, app):
        self.app = app
        self.engine = create_engine(self.app.config["database"])
        logging.debug("create_engine:{0}".format(self.app.config["database"]))
        self.Session = sessionmaker(bind=self.engine)

        # Mappings
        self.Base = declarative_base(bind=self.engine)

        class User(self.Base):
            __tablename__ = "user"
            uuid = Column(String(32), primary_key=True) # hex representation
            ipv4 = Column(Integer, index=True)
            # ipv6 addr strings are <= 45 bytes
            # http://stackoverflow.com/q/166132/130598
            ipv6 = Column(String(45), index=True)
            pings = relationship("Ping", backref="user")
            last_ping = relationship("Ping")
        self.User = User

        class Ping(self.Base):
            __tablename__ = "ping"
            id = Column(Integer, primary_key=True)
            uuid = Column(String(32), ForeignKey('user.uuid')) 
            time = Column(DateTime(timezone=True), index=True)
            controller = Column(String(20))
            version = Column(String(20))
            connections = Column(Integer)
            mean_connection_lifetime = Column(String(20))
        self.Ping = Ping

        self.Base.metadata.create_all()

    # Helpers

    @contextmanager
    def session_scope(self):
        s = self.Session()
        yield s
        try:
            s.commit()
        except:
            s.rollback()
            raise
        finally:
            s.close()
