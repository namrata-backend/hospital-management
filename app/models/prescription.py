from app import mongo
from datetime import datetime, timezone
from bson import ObjectId

class PrescriptionModel:

    @staticmethod
    def save_prescription(patient_id, doctor_id, diagnosis,
                          medicines, notes, followup_date):

        prescription = {
            "patient_id": ObjectId(patient_id),
            "doctor_id": ObjectId(doctor_id),
            "diagnosis": diagnosis,
            "medicines": medicines,
            "notes": notes,
            "followup_date": followup_date,
            "sms_sent": False,
            "created_at": datetime.now(timezone.utc)
        }

        result = mongo.db.prescriptions.insert_one(prescription)
        return str(result.inserted_id)

    @staticmethod
    def get_prescription_by_patient(patient_id):
        prescription = mongo.db.prescriptions.find_one(
            {"patient_id": ObjectId(patient_id)}
        )
        if prescription:
            prescription["_id"] = str(prescription["_id"])
            prescription["patient_id"] = str(prescription["patient_id"])
            prescription["doctor_id"] = str(prescription["doctor_id"])
            prescription["created_at"] = str(prescription["created_at"])
        return prescription

    @staticmethod
    def mark_sms_sent(prescription_id):
        mongo.db.prescriptions.update_one(
            {"_id": ObjectId(prescription_id)},
            {"$set": {"sms_sent": True}}
        )