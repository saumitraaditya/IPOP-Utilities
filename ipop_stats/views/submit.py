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
    logging.debug("Are we doing sth?")
    time = datetime.datetime.now()
    ip = request.remote_addr              # TODO: How does this work under wsgi?
    logging.debug("ip:{0}".format(ip))
    ip = validate_ip(ip)
    logging.debug("SOMTHING is posted")
    if ip:
        ipv6 = ":" in request.remote_addr
        ipv4 = not ipv6
    else:
        message = "IP address '%s' failed to validate" % ip
        app.logger.error(message)
        raise ApiFail(message, _ip_addr="bad format")
    logging.debug("say something ... ")
    logging.debug("request uuid:{0}".format(request.json["uuid"]))
    #client_uuid = uuid.UUID(hex=request.json["uuid"])
    client_uuid = uuid.UUID(request.json["uuid"])
    logging.debug("uuid:{0}".format(client_uuid))
    app.logger.debug("got ping from UUID %s" % client_uuid)
    logging.debug("say something more ... ")
    with app.database.session_scope() as session:
        #print session.query(app.database.Ping).all()
        #print session.query(app.database.User).all()
        #last_ping = session.query(app.database.Ping).select_from(app.database.User). \
        #    filter(app.database.User.uuid == uuid). \
        #    join(app.database.User.last_ping).first()
        user = app.database.User(uuid=str(client_uuid), ipv4=555, ipv6="abcdefghijklmn")
        ping = app.database.Ping(uuid=str(client_uuid))
        #session.add(user)
        session.add(ping)
        session.commit()

@submit.route("/generate_uuid")
def generate_uuid():
    """Convenience uuid generator, for clients who don't have a convenient local
    generator."""
    response = jsonify(result=uuid.uuid4().hex, status="success")
    response.headers["Expires"] = "-1"
    response.headers["Cache-Control"] = "no-cache, no-store"
    return response
