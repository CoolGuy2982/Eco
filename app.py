# app.py
from app import create_app

app = create_app()  # Create the app object
print("App object created:", app)

if __name__ == "__main__":
    app.run(debug=True)  # Run the app after it's created