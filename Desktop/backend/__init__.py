import flask
import time

def prints():
    print("hello")

def create_app():
    app = flask.Flask(__name__)
    app.config['SECRET_KEY'] = 'Mikehasamangina'
    
    from .app import app
    from .auth import auth
    
    app.register_blueprint(app, url_prefix = '/')
    app.register_blueprint(auth, url_prefix = '/')
    return app