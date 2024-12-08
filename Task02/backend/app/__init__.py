from flask import Flask
from flask_cors import CORS
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)  # Enable CORS for frontend access

    # Register routes
    from .routes import main
    app.register_blueprint(main)

    return app
