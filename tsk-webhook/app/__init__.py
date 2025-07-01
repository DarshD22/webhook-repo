from flask import Flask
from app.extensions import mongo
from app.webhook.routes import webhook
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Creating our Flask app
def create_app():
    app = Flask(__name__)

    # Set MongoDB URI from environment
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    
    
    # Ensure Mongo URI is set
    if not app.config["MONGO_URI"]:
        raise ValueError("MONGO_URI not set. Please define it in your environment or .env file.")

    # Initialize Mongo extension
    mongo.init_app(app)

    # Register all blueprints
    app.register_blueprint(webhook)
    
    return app
