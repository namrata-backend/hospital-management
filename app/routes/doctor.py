from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.patient import PatientModel
import json
from functools import wraps

doctor_bp = Blueprint("doctor", __name__)

def doctor_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        identity = json.loads(get_jwt_identity())
        if identity["role"] != "doctor":
            return jsonify({"error": "Doctor access only"}), 403
        return fn(*args, **kwargs)
    return wrapper


@doctor_bp.route("/queue", methods=["GET"])
@doctor_required
def get_queue():
    patients = PatientModel.get_waiting_patients()
    return jsonify({
        "total": len(patients),
        "waiting_patients": patients
    }), 200


@doctor_bp.route("/patient/<patient_id>/call", methods=["PATCH"])
@doctor_required
def call_patient(patient_id):
    patient = PatientModel.get_patient_by_id(patient_id)

    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    if patient["status"] != "waiting":
        return jsonify({
            "error": f"Patient is already {patient['status']}"
        }), 400

    PatientModel.update_status(patient_id, "called")

    return jsonify({
        "message": "Patient called successfully",
        "token_number": patient["token_number"],
        "name": patient["name"],
        "status": "called"
    }), 200


@doctor_bp.route("/patient/<patient_id>", methods=["GET"])
@doctor_required
def get_patient(patient_id):
    patient = PatientModel.get_patient_by_id(patient_id)

    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    PatientModel.update_status(patient_id, "in_consultation")

    return jsonify({"patient": patient}), 200