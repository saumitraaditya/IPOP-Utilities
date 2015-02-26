from flask import Flask
import yaml
import os.path
import logging.config
from database import Database

def create(config):
    """http://flask.pocoo.org/docs/patterns/appfactories/"""

    app = Flask(__name__.split('.')[0])

    # Load YAML config into app.config
    if not isinstance(config, dict):
        with open(os.path.join(app.instance_path, config)) as f:
            config = yaml.load(f)
    config.update({k.upper(): v for k, v in config["flask"].items()})
    app.config.update(config)
    del config
    
    # Configure logging
    logging.config.dictConfig(app.config["logging"])

    # Initialize database
    app.database = Database(app)

    # Load blueprints
    from .views.submit import submit
    app.register_blueprint(submit)

    if False and app.debug:
        app.logger.warning("Debug mode is on. Do not use this in production.")
        from .views.debug import debug
        app.register_blueprint(debug)

    return app
