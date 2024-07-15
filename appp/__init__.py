from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_default_secret_key')
    google_maps_api = os.getenv('GOOGLE_MAPS_API')
    app.config['GOOGLE_MAPS_API_KEY'] = google_maps_api

    from .routes import main
    app.register_blueprint(main)

    return app
