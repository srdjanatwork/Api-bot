# -*- coding: utf-8 -*-
import json

from .. import app, public_bp


@app.errorhandler(Exception)
def exception_handler(error):
    msg = repr(error)
    app.logger.error(msg)
    return app.response_class(
        response='Internal Error: {0}'.format(msg),
        status=500,
        mimetype='text/plain')


@public_bp.route('/', endpoint='root')
def version():
    try:
        app_version = json.load(open("/usr/src/app/version.json"))['version']
    except FileNotFoundError:
        app_version = "Local server"
    return app.response_class(
        response='API version {0}'.format(app_version),
        status=200,
        mimetype='text/plain')


@public_bp.route('/monitor', endpoint='monitor')
def monitor():
    return app.response_class(
        response='Ok',
        status=200,
        mimetype='text/plain')
