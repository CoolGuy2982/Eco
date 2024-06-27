from appp import create_app

app = create_app()  # Create the app object

if __name__ == "__main__":
    app.run(debug=True)  # Run the app after it's created