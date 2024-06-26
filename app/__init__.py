from flask import Flask
import os

def create_app():
    print("Creating Flask app...")
    app = Flask(__name__)
    app.config['GOOGLE_MAPS_API_KEY'] = os.getenv('GOOGLE_MAPS_API')
    app.config['AQ_MAPS_API_KEY'] = os.getenv('AQ_MAPS_API')

    # Import and register the blueprint from the routes module
    from .routes import main
    app.register_blueprint(main)

    print("Flask app created successfully.")
    return app
