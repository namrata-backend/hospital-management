from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.patient import PatientModel
import json
from functools import wraps

nurse_bp = Blueprint("nurse", __name__)

def nurse_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        identity = json.loads(get_jwt_identity())
        if identity["role"] != "nurse":
            return jsonify({"error": "Nurse access only"}), 403
        return fn(*args, **kwargs)
    return wrapper


@nurse_bp.route("/patient/add", methods=["POST"])
@nurse_required
def add_patient():
    identity = json.loads(get_jwt_identity())
    nurse_id = identity["user_id"]

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name")
    age = data.get("age")
    gender = data.get("gender")
    mobile_number = data.get("mobile_number")
    chief_complaint = data.get("chief_complaint")

    if not all([name, age, gender, mobile_number, chief_complaint]):
        return jsonify({"error": "All fields are required"}), 400

    if gender not in ["male", "female", "other"]:
        return jsonify({
            "error": "Gender must be male, female or other"
        }), 400

    patient_id, token_number = PatientModel.add_patient(
        name, age, gender, mobile_number, chief_complaint, nurse_id
    )

    return jsonify({
        "message": "Patient added successfully",
        "patient_id": patient_id,
        "token_number": token_number
    }), 201


@nurse_bp.route("/queue", methods=["GET"])
@nurse_required
def get_queue():
    patients = PatientModel.get_todays_queue()
    return jsonify({
        "total": len(patients),
        "queue": patients
    }), 200