from appp import create_app
# this file is to run the app, it calls the blueprint of main from init, which calls from route. All this is done so it is modular.
app = create_app()  # create the app object

if __name__ == "__main__":
    app.run(debug=True)  # run the app after it's created