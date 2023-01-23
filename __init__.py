import flask
import time

def prints():
    print("hello")

def create_app():
    app = flask.Flask(__name__)
    app.config['SECRET_KEY'] = 'Mikehasamangina'
    
    from golfappbackend.views import views
    from golfappbackend.auth import auth
    
    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(auth, url_prefix = '/')
    return app