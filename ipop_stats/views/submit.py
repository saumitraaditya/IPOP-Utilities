from ..errors import *
from flask import Blueprint, request, jsonify
from flask import current_app as app
from sqlalchemy import func
import datetime
import socket
import uuid

def validate_ip(ip):
    """Returns a compressed IP representation if the IP is valid, otherwise
    False. It's implemented using the ``socket`` module for compatibility."""
    try:
        return socket.ntop(socket.AF_INET, socket.pton(socket.AF_INET, ip))
    except socket.error:
        try:
            return socket.ntop(socket.AF_INET6,
                               socket.pton(socket.AF_INET6, ip))
        except socket.error:
            return False

submit = Blueprint("submit", __name__, url_prefix="/api")

@submit.route("/submit", methods=["POST"])
def update():
    time = datetime.datetime()
    ip = request.remote_addr              # TODO: How does this work under wsgi?
    ip = validate_ip(ip)
    if ip:
        ipv6 = ":" in request.remote_addr
        ipv4 = not ipv6
    else:
        message = "IP address '%s' failed to validate" % ip
        app.logger.error(message)
        raise ApiFail(message, _ip_addr="bad format")
    client_uuid = uuid.UUID(hex=request.json["uuid"])
    app.logger.debug("got ping from UUID %s" % client_uuid)
    with app.database.session_scope() as session:
        last_ping = session.query(database.Ping).select_from(database.User). \
            filter(database.User.uuid == uuid). \
            join(database.User.last_ping).first()

@submit.route("/generate_uuid")
def generate_uuid():
    """Convenience uuid generator, for clients who don't have a convenient local
    generator."""
    response = jsonify(result=uuid.uuid4().hex, status="success")
    response.headers["Expires"] = "-1"
    response.headers["Cache-Control"] = "no-cache, no-store"
    return response
