from flask import Flask
import os

def create_app():
    app = Flask(__name__)

    google_maps_api = os.getenv('GOOGLE_MAPS_API')
    app.config['GOOGLE_MAPS_API_KEY'] = google_maps_api

    from .routes import main
    app.register_blueprint(main)

    return app
