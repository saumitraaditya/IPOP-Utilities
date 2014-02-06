from flask import current_app, Blueprint, request
import database
import datetime
import socket

def validate_ip(ip):
    """Returns a compressed IP representation if the IP is valid, otherwise
    False. It's implemented using the ``socket`` module for Python 3.2
    compatibility."""
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
    ip = request.remote_addr # TODO: How does this work under wsgi?
    if (ip = validate_ip(ip)):
        ipv6 = ":" in request.remote_addr
        ipv4 = not ipv6
    else:
        current_app.logger.error("IP address '%s' failed to validate" % ip)
    uuid = request.json["uuid"]
