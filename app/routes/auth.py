from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models.user import UserModel

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    # Validate required fields
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not all([name, email, password, role]):
        return jsonify({"error": "All fields are required"}), 400

    if role not in ["nurse", "doctor"]:
        return jsonify({"error": "Role must be nurse or doctor"}), 400

    # Create user
    user_id, error = UserModel.create_user(name, email, password, role)

    if error:
        return jsonify({"error": error}), 409

    return jsonify({
        "message": "User registered successfully",
        "user_id": user_id
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return jsonify({"error": "Email and password required"}), 400

    # Find user by email
    user = UserModel.find_by_email(email)
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    # Verify password
    if not UserModel.verify_password(password, user["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    # Create JWT token
    access_token = create_access_token(identity={
        "user_id": str(user["_id"]),
        "role": user["role"],
        "name": user["name"]
    })

    return jsonify({
        "access_token": access_token,
        "role": user["role"],
        "name": user["name"]
    }), 200