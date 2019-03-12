import os
from flask import Flask
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask import current_app, g
from flask.cli import with_appcontext
from flask import session


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev'
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello

    from . import db
    from . import login
    app.register_blueprint(login.bp)
    from . import home
    app.register_blueprint(home.bp)
    from . import joblist
    app.register_blueprint(joblist.bp)
    from . import details
    app.register_blueprint(details.bp)
    from . import clientJobs
    app.register_blueprint(clientJobs.bp)
    from . import jobDetails
    app.register_blueprint(jobDetails.bp)
    from . import addJob
    app.register_blueprint(addJob.bp)
    from . import addExistingJob
    app.register_blueprint(addExistingJob.bp)
    from . import applicationlist
    app.register_blueprint(applicationlist.bp)
    from . import applicationviewclient
    app.register_blueprint(applicationviewclient.bp)
    from . import applicationview
    app.register_blueprint(applicationview.bp)
    from . import codingtest
    app.register_blueprint(codingtest.bp)
    from . import apply
    app.register_blueprint(apply.bp)

    from . import loginClient
    app.register_blueprint(loginClient.bp)

    return app
