from ..errors import *
from flask import Blueprint, request, jsonify
from flask import current_app as app
from sqlalchemy import func
import datetime
import socket
import uuid
import logging

def validate_ip(ip):
    """Returns a compressed IP representation if the IP is valid, otherwise
    False. It's implemented using the ``socket`` module for compatibility."""
    try:
        return socket.inet_ntop(socket.AF_INET, socket.inet_pton(socket.AF_INET, ip))
    except socket.error:
        try:
            return socket.ntop(socket.AF_INET6,
                               socket.pton(socket.AF_INET6, ip))
        except socket.error:
            return False

submit = Blueprint("submit", __name__, url_prefix="/api")

@submit.route("/submit", methods=["POST"])
def update():
    time = datetime.datetime.now()
    ip = request.remote_addr              # TODO: How does this work under wsgi?
    ip = validate_ip(ip)
    if ip:
        ipv6 = ":" in request.remote_addr
        ipv4 = not ipv6
    else:
        message = "IP address '%s' failed to validate" % ip
        app.logger.error(message)
        raise ApiFail(message, _ip_addr="bad format")
    uid = request.json["uid"]
    with app.database.session_scope() as session:
        user = session.query(app.database.User).\
               filter(app.database.User.uid == uid).first()
        if user == None:   
            user = app.database.User(uid=uid, ipv4=request.json["ipv4"],\
                                     ipv6=request.json["ipv6"])
        elif user.ipv4 != request.json["ipv4"] and\
             user.ipv6 != request.json["ipv6"]:
            response = jsonify(result=uuid.uuid4().hex, status="error")
            return response

        ping = app.database.Ping(uid=uid, time=datetime.datetime.strptime(\
            request.json["time"], "%Y-%m-%d %H:%M:%S.%f"),\
            controller=request.json["controller"],\
            version=request.json["version"])
        session.add(user)
        session.add(ping)
        session.commit()

    response = jsonify(result=uuid.uuid4().hex, status="success")
    return response

@submit.route("/")
def hello():
    return "Hello World!"

@submit.route("/generate_uuid")
def generate_uuid():
    """Convenience uuid generator, for clients who don't have a convenient local
    generator."""
    response = jsonify(result=uuid.uuid4().hex, status="success")
    response.headers["Expires"] = "-1"
    response.headers["Cache-Control"] = "no-cache, no-store"
    return response
