from app import mongo

def generate_token_number():
    # Count how many patients registered today
    from datetime import datetime, timezone

    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    count = mongo.db.patients.count_documents({
        "arrived_at": {"$gte": today_start}
    })

    # Generate token like T-001, T-002
    token_number = f"T-{str(count + 1).zfill(3)}"
    return token_number