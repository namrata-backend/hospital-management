import os

def send_prescription_sms(mobile_number, patient_name,
                           diagnosis, medicines):
    try:
        # Build SMS message
        medicine_list = ""
        for med in medicines:
            medicine_list += f"{med['name']} - {med['dose']} - {med['frequency']}\n"

        message = f"""
Dear {patient_name},
Your prescription from clinic:

Diagnosis: {diagnosis}

Medicines:
{medicine_list}
Please follow doctor's advice.
        """.strip()

        # ---- TWILIO INTEGRATION ----
        # Uncomment below when you signup on twilio.com
        # and add these to your .env file:
        # TWILIO_ACCOUNT_SID=your_sid
        # TWILIO_AUTH_TOKEN=your_token
        # TWILIO_PHONE_NUMBER=your_twilio_number

        # from twilio.rest import Client
        # client = Client(
        #     os.getenv("TWILIO_ACCOUNT_SID"),
        #     os.getenv("TWILIO_AUTH_TOKEN")
        # )
        # client.messages.create(
        #     body=message,
        #     from_=os.getenv("TWILIO_PHONE_NUMBER"),
        #     to=f"+91{mobile_number}"
        # )

        # For now we print the message (simulate SMS)
        print(f"\n--- SMS TO {mobile_number} ---")
        print(message)
        print(f"--- END SMS ---\n")

        return True, None

    except Exception as e:
        return False, str(e)