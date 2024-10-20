from appp import create_app

app = create_app()  # create the app object

if __name__ == "__main__":
    app.run(debug=True)  # run the app after it's created