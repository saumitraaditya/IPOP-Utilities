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
    xmpp_host = request.json["xmpp_host"]
    with app.database.session_scope() as session:

        first_xmpp = False
        first_user = False

        xmpp = session.query(app.database.Xmpp).\
               filter(app.database.Xmpp.xmpp_host == xmpp_host).first()
        if xmpp == None:   
            xmpp = app.database.Xmpp(xmpp_host=xmpp_host)
            first_xmpp = True
        session.add(xmpp)
        session.flush()

        user = session.query(app.database.User).\
               filter(app.database.User.uid == uid).first()
        if user == None:   
            user = app.database.User(uid=uid, ipv4=request.json["ipv4"],\
                     ipv6=request.json["ipv6"],\
                     xmpp_username=request.json["xmpp_username"])
            first_user = True
        elif user.ipv4 != request.json["ipv4"] and\
             user.ipv6 != request.json["ipv6"]:
            response = jsonify(result=uuid.uuid4().hex, status="error")
            return response
        user.xmpp_host = xmpp.id 
        session.add(user)
        session.flush()

        ping = app.database.Ping(\
            time=datetime.datetime.strptime(request.json["time"], "%Y-%m-%d %H:%M:%S.%f"), controller=request.json["controller"],\
            version=request.json["version"], xmpp_host=xmpp.id, uid=user.id)
        session.add(ping)
        session.flush()

        user.last_ping = ping.id
        xmpp.last_ping = ping.id
        if first_xmpp:
            xmpp.first_ping = ping.id
        if first_user:
            user.first_ping = ping.id
        session.add(user) 
        session.add(xmpp)
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
