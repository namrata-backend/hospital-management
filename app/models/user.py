from app import mongo
import bcrypt
from bson import ObjectId

class UserModel:

    @staticmethod
    def create_user(name, email, password, role):
        # Check if email already exists
        existing_user = mongo.db.users.find_one({"email": email})
        if existing_user:
            return None, "Email already exists"

        # Hash the password
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        # Build user document
        user = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "role": role
        }

        # Insert into MongoDB
        result = mongo.db.users.insert_one(user)
        return str(result.inserted_id), None

    @staticmethod
    def find_by_email(email):
        return mongo.db.users.find_one({"email": email})

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password
        )