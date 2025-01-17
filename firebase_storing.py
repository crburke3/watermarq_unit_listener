from datetime import datetime
from typing import List
import helpers
from RoomSearch import RoomSearch
from RunLog import RunLog
from Unit import Unit
import os
import firebase_admin
from firebase_admin import credentials, firestore
import json
from dotenv import load_dotenv
load_dotenv()


# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    service_account_path = "serviceAccount.json"
    if os.path.exists(service_account_path):
        print("The serviceAccount.json file exists.")
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)
    else:
        print("The serviceAccount.json file does not exist. Initializing from ENV")
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
    print("loading units from firebase...")
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


def save_room_searches(room_searches: List[RoomSearch]):
    # Reference to the "watermarq_system" collection and "room_searches" document
    doc_ref = db.collection("watermarq_system").document("room_searches")
    room_search_dicts = [room_search.to_dict() for room_search in room_searches]
    doc_ref.set({
        'room_searches': room_search_dicts
    })
    print(f"Successfully saved {len(room_search_dicts)} room searches to Firestore.")


def load_room_searches() -> List[RoomSearch]:
    # Reference to the "watermarq_system" collection and "room_searches" document
    collection_ref = db.collection("watermarq_system").document("temp_search_main").collection('temp_searches')
    query = collection_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1)
    results = query.stream()
    searches:[RoomSearch] = []
    for doc in results:
        doc_data = doc.to_dict()
        search = RoomSearch.from_dict(doc_data)
        searches.append(search)
    # Get the document
    print(f"Successfully loaded {len(searches)} room searches.")
    return searches


def save_run_log_to_firebase(successful: bool, error: str=None):
    collection_ref = db.collection("watermarq_system").document("run_logs").collection('logs')
    log = RunLog(timestamp=datetime.now(), success=successful, error_message=error)
    log_data = log.to_dict()
    collection_ref.add(log_data)
    print("Run log saved to Firebase.")


def get_most_recent_run_log():
    collection_ref = db.collection("watermarq_system").document("run_logs").collection('logs')
    query = collection_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1)
    results = query.stream()
    for doc in results:
        log_data = doc.to_dict()
        return RunLog.from_dict(log_data)
    return None


def save_search_args(phone_number: str, room_counts: [int] = None, only_exterior: bool=None, max_price:int=None):
    args_ref = db.collection("watermarq_system").document("temp_search_main").collection('temp_searches')
    doc_ref = args_ref.document(phone_number)
    search_doc = doc_ref.get()
    if search_doc.exists:
        search_data = search_doc.to_dict()
        search = RoomSearch.from_dict(search_data)
    else:
        search = RoomSearch(phones=[phone_number])

    if room_counts:
        search.num_rooms = room_counts
    if only_exterior:
        search.only_exterior = only_exterior
    if max_price:
        print("need to set max price up")

    search_export = search.to_dict()
    doc_ref.set(search_export)
    return search


def get_search(phone_number: str):
    args_ref = db.collection("watermarq_system").document("temp_search_main").collection('temp_searches')
    doc_ref = args_ref.document(phone_number)
    search_doc = doc_ref.get()
    if search_doc.exists:
        search_data = search_doc.to_dict()
        search = RoomSearch.from_dict(search_data)
        return search
    else:
        return None


def delete_search(phone_number: str):
    args_ref = db.collection("watermarq_system").document("temp_search_main").collection('temp_searches')
    doc_ref = args_ref.document(phone_number)
    doc_ref.delete()

# save_room_searches([
#             RoomSearch(
#                 name="christian and jake",
#                 phones=['+17048062009',
#                         '+19802152772'],
#                 num_rooms=[2, 3],
#                 only_exterior=True
#             ),
#             RoomSearch(
#                 name="Andrea & Drew",
#                 phones=["+19806364444",
#                         "+19198277295"],
#                 num_rooms=[1],
#                 only_exterior=False
#             ),
#             RoomSearch(
#                 name="Acacia",
#                 phones=[
#                     '+14256916189'
#                 ],
#                 num_rooms=[1],
#                 only_exterior=False
#             ),
#             RoomSearch(
#                 name="Marcus",
#                 phones=[
#                     '+12537364084'
#                 ],
#                 num_rooms=[1],
#                 only_exterior=False
#             )
#         ])