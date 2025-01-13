from datetime import datetime
import helpers
from Unit import Unit
import os
import firebase_admin
from firebase_admin import credentials, firestore
import json
# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    service_account_path = "serviceAccount.json"
    if os.path.exists(service_account_path):
        print("The shnitserviceAccount.json file exists.")
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)
    else:
        print("The shnitserviceAccount.json file does not exist. Initializing from ENV")
        # Retrieve the Firebase account details from the .env file
        firebase_account = os.getenv('firebase_account')
        if firebase_account:
            # If the environment variable exists, initialize from it
            try:
                # Assuming firebase_account contains the JSON string for credentials
                cred = credentials.Certificate(json.loads(firebase_account))
                firebase_admin.initialize_app(cred)
                print("Firebase initialized from ENV.")
            except ValueError as e:
                print(f"Error initializing Firebase from ENV: {e}")
        else:
            print("No firebase_account found in .env. Cannot initialize Firebase.")


firebase_db_path = "/old_units"
db = firestore.client()
ref = db.collection("watermarq_system").document("old_units")


def load_units_from_firebase():
    try:
        # Fetch data from Firebase Realtime Database
        doc = ref.get()

        if not doc.exists:
            print(f"Error: No data found at {firebase_db_path}.")
            return None, []

        # Extract last updated timestamp and units
        data = doc.to_dict()
        last_updated = data.get('last_updated', None)
        if last_updated:
            parsed_datetime = datetime.fromisoformat(last_updated)
        else:
            parsed_datetime = None

        units_data = data.get('units', [])

        # Convert the JSON data into Unit objects
        units = [Unit.from_json(unit) for unit in units_data]

        # Optional: add CSV data if needed
        for unit in units:
            helpers.add_csv_data(unit)

        return parsed_datetime, units

    except Exception as e:
        print(f"Error loading data from Firebase: {e}")
        return None, []


def save_units_to_firebase(units):
    last_updated = datetime.utcnow().isoformat()
    data = {
        'last_updated': last_updated,
        'units': [unit.to_dict() for unit in units]
    }

    try:
        # Save data to Firebase Realtime Database
        ref.set(data)  # This will overwrite the data at the specified path

        print(f"Units successfully saved to Firebase at {firebase_db_path}.")
    except Exception as e:
        print(f"Error saving data to Firebase: {e}")


