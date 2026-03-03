from app import mongo
from datetime import datetime, timezone
from bson import ObjectId
from app.services.queue_service import generate_token_number

class PatientModel:

    @staticmethod
    def add_patient(name, age, gender, mobile_number, 
                    chief_complaint, nurse_id):
        
        # Auto generate token number
        token_number = generate_token_number()

        # Build patient document
        patient = {
            "token_number": token_number,
            "name": name,
            "age": age,
            "gender": gender,
            "mobile_number": mobile_number,
            "chief_complaint": chief_complaint,
            "status": "waiting",
            "added_by": ObjectId(nurse_id),
            "arrived_at": datetime.now(timezone.utc)
        }

        result = mongo.db.patients.insert_one(patient)
        return str(result.inserted_id), token_number

    @staticmethod
    def get_todays_queue():
        from datetime import datetime, timezone

        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        patients = mongo.db.patients.find(
            {"arrived_at": {"$gte": today_start}},
            {"password": 0}
        ).sort("arrived_at", 1)

        result = []
        for patient in patients:
            patient["_id"] = str(patient["_id"])
            patient["added_by"] = str(patient["added_by"])
            patient["arrived_at"] = str(patient["arrived_at"])
            result.append(patient)

        return result

    @staticmethod
    def get_waiting_patients():
        patients = mongo.db.patients.find(
            {"status": "waiting"}
        ).sort("arrived_at", 1)

        result = []
        for patient in patients:
            patient["_id"] = str(patient["_id"])
            patient["added_by"] = str(patient["added_by"])
            patient["arrived_at"] = str(patient["arrived_at"])
            result.append(patient)

        return result

    @staticmethod
    def get_patient_by_id(patient_id):
        patient = mongo.db.patients.find_one(
            {"_id": ObjectId(patient_id)}
        )
        if patient:
            patient["_id"] = str(patient["_id"])
            patient["added_by"] = str(patient["added_by"])
            patient["arrived_at"] = str(patient["arrived_at"])
        return patient

    @staticmethod
    def update_status(patient_id, status):
        mongo.db.patients.update_one(
            {"_id": ObjectId(patient_id)},
            {"$set": {"status": status}}
        )