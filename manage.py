from connexion import FlaskApp

app = FlaskApp(__name__)
app.add_api("openapi.yaml")
app.run()
