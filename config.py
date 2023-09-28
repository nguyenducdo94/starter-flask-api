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
    facebook_account_manager_collection = db["facebook_account_manager"]
    fb_check_new_post_scheduler_collection = db["fb_check_new_post_scheduler"]

    return app, login_manager, users_collection, facebook_account_manager_collection, fb_check_new_post_scheduler_collection

app, login_manager, users_collection, facebook_account_manager_collection, fb_check_new_post_scheduler_collection = create_app()


import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('yellow-springbok-fezCyclicDB')