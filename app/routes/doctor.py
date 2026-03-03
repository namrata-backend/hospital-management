from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.patient import PatientModel
from app.models.prescription import PrescriptionModel
from app.services.sms_service import send_prescription_sms
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

@doctor_bp.route("/prescription/save", methods=["POST"])
@doctor_required
def save_prescription():
    identity = json.loads(get_jwt_identity())
    doctor_id = identity["user_id"]

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    patient_id = data.get("patient_id")
    diagnosis = data.get("diagnosis")
    medicines = data.get("medicines")
    notes = data.get("notes", "")
    followup_date = data.get("followup_date", "")

    if not all([patient_id, diagnosis, medicines]):
        return jsonify({
            "error": "patient_id, diagnosis and medicines are required"
        }), 400

    if not isinstance(medicines, list) or len(medicines) == 0:
        return jsonify({
            "error": "medicines must be a non empty list"
        }), 400

    # Check patient exists
    patient = PatientModel.get_patient_by_id(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    # Save prescription to MongoDB
    prescription_id = PrescriptionModel.save_prescription(
        patient_id, doctor_id, diagnosis,
        medicines, notes, followup_date
    )

    # Update patient status to done
    PatientModel.update_status(patient_id, "done")

    # Send SMS to patient
    sms_success, sms_error = send_prescription_sms(
        patient["mobile_number"],
        patient["name"],
        diagnosis,
        medicines
    )

    # Mark SMS sent in DB if successful
    if sms_success:
        PrescriptionModel.mark_sms_sent(prescription_id)

    return jsonify({
        "message": "Prescription saved successfully",
        "prescription_id": prescription_id,
        "sms_sent": sms_success,
        "patient_status": "done"
    }), 201