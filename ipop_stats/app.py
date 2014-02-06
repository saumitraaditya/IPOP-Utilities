from flask import Flask

def create_app(config):
    """http://flask.pocoo.org/docs/patterns/appfactories/"""
    app = Flask(__name__.split('.')[0])
    app.config.from_pyfile(config)

    from .views.submit import submit
    app.register_blueprint(submit)

    if app.debug:
        app.logger.warning("Debug mode is on. Do not use this in production.")
        from .views.debug import debug
        app.register_blueprint(debug)

    return app
