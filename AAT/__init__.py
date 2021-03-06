import os

from flask import Flask
from flask_jsglue import JSGlue

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    jsglue = JSGlue()
    jsglue.init_app(app)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        DATABASE=os.environ.get('DATABASE_URL')
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import account
    app.register_blueprint(account.bp)

    from . import zoomAPI
    app.register_blueprint(zoomAPI.bp)
    app.add_url_rule('/', endpoint='index')

    return app