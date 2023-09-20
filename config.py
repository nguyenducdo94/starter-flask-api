from flask import Flask
from flask_login import LoginManager
import pymongo

def create_app():
    app = Flask(__name__)
    app.secret_key = 'facebook_tool_secret_key'

    login_manager = LoginManager()
    login_manager.login_view = 'login'  # Set the view function for login
    login_manager.init_app(app)

    # MongoDB Configuration
    mongo_client = pymongo.MongoClient("mongodb+srv://aifone:ale12345@cluster0.enfnrew.mongodb.net/?retryWrites=true&w=majority")
    db = mongo_client["onlinetool"]
    users_collection = db["users"]

    return app, login_manager, users_collection

app, login_manager, users_collection = create_app()