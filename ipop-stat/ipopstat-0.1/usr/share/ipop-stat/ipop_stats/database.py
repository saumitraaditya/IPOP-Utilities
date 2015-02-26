from sqlalchemy import create_engine, Column, String, Integer, DateTime,\
                       ForeignKey, Binary
from sqlalchemy.orm import sessionmaker, relationship, backref
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

        class Xmpp(self.Base):
            __tablename__ = "xmpp"
            id = Column(Integer, primary_key=True)
            xmpp_host = Column(String(40))
            first_ping = Column(Integer)
            last_ping = Column(Integer)
        self.Xmpp = Xmpp

        class User(self.Base):
            __tablename__ = "user"
            id = Column(Integer, primary_key=True)
            uid = Column(String(40)) # hex representation
            xmpp_username = Column(String(40))
            xmpp_host = Column(Integer, ForeignKey('xmpp.id'))
            ipv4 = Column(Integer, index=True)
            ipv6 = Column(String(45), index=True)
            first_ping = Column(Integer)
            last_ping = Column(Integer)
        self.User = User

        class Ping(self.Base):
            __tablename__ = "ping"
            id = Column(Integer, primary_key=True)
            uid = Column(String(40), ForeignKey('user.uid')) 
            xmpp_host = Column(Integer, ForeignKey('xmpp.id'))
            time = Column(DateTime(timezone=True), index=True)
            controller = Column(String(20))
            version = Column(String(20))
        self.Ping = Ping

        if self.app.config["new_database"]:
            self.Base.metadata.drop_all()
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
