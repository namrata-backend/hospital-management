from flask import Flask
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from config import Config

# These will be accessible from anywhere in the app
mongo = None
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    # Load config
    app.config["MONGO_URI"] = Config.MONGO_URI
    app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY

    # Connect to MongoDB
    global mongo
    client = MongoClient(Config.MONGO_URI)
    mongo = client
    mongo.db = client.get_default_database()

    # Initialize JWT with app
    jwt.init_app(app)

    # Register blueprints (routes)
    from app.routes.auth import auth_bp
    from app.routes.nurse import nurse_bp
    from app.routes.doctor import doctor_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(nurse_bp, url_prefix="/api/nurse")
    app.register_blueprint(doctor_bp, url_prefix="/api/doctor")

    return app