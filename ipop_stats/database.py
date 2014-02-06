from flask import current_app
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import uuid
import functools

engine_url = current_app.config["DATABASE"]
engine = create_engine(engine_url)
Session = sessionmaker(bind=engine)

# Mappings
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    uuid = Column(String(32), primary_key=True) # hex representation
    ipv4 = Column(Integer, index=True)
    # ipv6 addr strings are <= 45 bytes http://stackoverflow.com/q/166132/130598
    ipv6 = Column(String(45), index=True)
    pings = relationship("Ping", backref="user")

class Ping(Base):
    __tablename__ = "pings"
    time = Column(DateTime(timezone=True), index=True)
    controller = Column(String(20))
    version = Column(String(20))
    connections = Column(Integer)
    mean_connection_lifetime = Column(String(20))

Base.create_all()

# Helpers

def with_session(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        s = Session()
        try:
            result = f(s, *args, **kwargs)
            s.commit()
            return result
        except:
            s.rollback()
            raise
    return wrapper
