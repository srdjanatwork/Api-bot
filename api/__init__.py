# -*- coding: utf-8 -*-

import os
import time
import logging
import logging.config

from flask import Flask, Blueprint
from flask_cors import CORS

from .mongodb import db_url
from .utils import CustomJSONEncoder


def create_app():
    app = Flask(__name__)

    # TODO: Disable this in PROD
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['UPLOAD_FOLDER'] = '/tmp'
    app.debug = True

    # Logging
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    app.logger.info("Database: {0}".format(db_url))

    app.json_encoder = CustomJSONEncoder
    app.url_map.strict_slashes = False
    CORS(app)

    return app


class LogTimeFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            if "%Q" in datefmt:
                msec = "%03d" % record.msecs
                datefmt = datefmt.replace("%Q", msec)
            s = time.strftime(datefmt, ct)
        return s


def register_logger(app):
    gunicorn_logger = logging.getLogger('gunicorn.error')

    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))


logging.config.fileConfig('logging.conf')

app = create_app()
register_logger(app)

# Create all blueprints
public_bp = Blueprint('public', __name__)
resource_bp = Blueprint('resource', __name__)

# Register routes
from . import endpoints
from .endpoints import resource


def register_bluprints(app):
    # Public
    app.register_blueprint(public_bp)

    # Resources
    app.register_blueprint(resource_bp, url_prefix='/resources')


register_bluprints(app)