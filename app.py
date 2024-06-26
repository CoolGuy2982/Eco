from app import create_app
from flask_cors import CORS
import os

apply = create_app()
CORS(apply)  # Enable CORS for all routes and origins

if __name__ == "__main__":
    apply.run(debug=True)