from datetime import datetime
import helpers
from Unit import Unit

import firebase_admin
from firebase_admin import credentials
from firebase_admin import credentials, firestore

# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccount.json")
    firebase_admin.initialize_app(cred)


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


