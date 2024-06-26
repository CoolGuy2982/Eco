from flask import Flask
import os

def create_app():
    print("Creating Flask app...")
    app = Flask(__name__)
    google_maps_api = os.getenv('GOOGLE_MAPS_API')
    aq_maps_api = os.getenv('AQ_MAPS_API')
    print(f"GOOGLE_MAPS_API: {google_maps_api}")
    print(f"AQ_MAPS_API: {aq_maps_api}")
    app.config['GOOGLE_MAPS_API_KEY'] = google_maps_api
    app.config['AQ_MAPS_API_KEY'] = aq_maps_api

    # Import and register the blueprint from the routes module
    from .routes import main
    app.register_blueprint(main)

    print("Flask app created successfully.")
    return app
