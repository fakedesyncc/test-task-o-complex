from flask import Flask
from .database import init_db

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['DATABASE'] = 'weather.db'
    
    with app.app_context():
        init_db()
    
    from . import routes
    app.register_blueprint(routes.bp)
    
    return app