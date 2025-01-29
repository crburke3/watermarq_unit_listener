from datetime import datetime
from typing import List
import helpers
from RoomSearch import RoomSearch, UnitInterest
from RunLog import RunLog
from Unit import Unit
import os
import firebase_admin
from firebase_admin import credentials, firestore
import json
from dotenv import load_dotenv
load_dotenv()


# Initialize Firebase if not already initialized
def get_google_creds():
    if not firebase_admin._apps:
        service_account_path = "serviceAccount.json"
        if os.path.exists(service_account_path):
            print("The serviceAccount.json file exists.")
            cred = credentials.Certificate(service_account_path)
            return cred
        else:
            print("The serviceAccount.json file does not exist. Initializing from ENV")
            # Retrieve the Firebase account details from the .env file
            firebase_account = os.getenv('firebase_account_2')
            if firebase_account:
                # If the environment variable exists, initialize from it
                try:
                    # Assuming firebase_account contains the JSON string for credentials
                    cred = credentials.Certificate(json.loads(firebase_account))
                    print("Firebase creds from ENV.")
                    return cred
                except ValueError as e:
                    print(f"Error initializing creds from ENV: {e}")
            else:
                print("No firebase_account found in .env. Cannot initialize Firebase.")


cred = get_google_creds()
firebase_admin.initialize_app(cred)
firebase_db_path = "/old_units"
db = firestore.client()
main_collection = db.collection("watermarq_system")
old_units_ref = main_collection.document("old_units")
sublease_units_ref = main_collection.document("sublease_units")
args_collection = main_collection.document("temp_search_main").collection('temp_searches')
unit_change_collection = main_collection.document("search_changes_main").collection("search_changes")

def load_units_from_firebase(sublease=False):
    print("loading units from firebase...")
    try:
        # Fetch data from Firebase Realtime Database
        if sublease:
            doc = sublease_units_ref.get()
        else:
            doc = old_units_ref.get()

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

        if sublease:
            units = [x for x in units if x.is_sublease]

        return parsed_datetime, units

    except Exception as e:
        print(f"Error loading data from Firebase: {e}")
        return None, []


def save_unit_interest(from_number: str, unit_number: str):
    search = get_search(from_number)
    if not search.interested_units:
        search.interested_units = []
    existing_interest = next((interest for interest in search.interested_units if interest.unit_number == unit_number), None)
    if not existing_interest:
        existing_interest = UnitInterest(unit_number=unit_number, interest_count=1)
        search.interested_units.append(existing_interest)
    else:
        existing_interest.interest_count += 1
    save_search(phone_number=from_number, search=search)
    return search


def save_units_to_firebase(units, sublease=False):
    last_updated = datetime.utcnow().isoformat()
    data = {
        'last_updated': last_updated,
        'units': [unit.to_dict() for unit in units]
    }

    try:
        # Save data to Firebase Realtime Database
        if sublease:
            non_sublease_units = [x for x in units if not x.is_sublease]
            if len(non_sublease_units) > 0:
                raise Exception(f'You are attempting to save {len(non_sublease_units)} non sublease units to the sublease section')
            sublease_units_ref.set(data)
        else:
            sub_units = [x for x in units if x.is_sublease]
            if len(sub_units) > 0:
                raise Exception(
                    f'You are attempting to save {len(sub_units)} sublease units to the normal units section')
            old_units_ref.set(data)  # This will overwrite the data at the specified path
        print(f"Units successfully saved to Firebase at {firebase_db_path}.")
    except Exception as e:
        print(f"Error saving data to Firebase: {e}")


def save_room_searches(room_searches: List[RoomSearch]):
    for search in room_searches:
        save_search_args(search.phones[0], room_counts=search.num_rooms, only_exterior=search.only_exterior, name=search.name)


def load_room_searches() -> List[RoomSearch]:
    # Reference to the "watermarq_system" collection and "room_searches" document
    collection_ref = db.collection("watermarq_system").document("temp_search_main").collection('temp_searches')
    # query = collection_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1)
    results = collection_ref.stream()
    searches:[RoomSearch] = []
    for doc in results:
        doc_data = doc.to_dict()
        search = RoomSearch.from_dict(doc_data)
        searches.append(search)
    # Get the document
    print(f"Successfully loaded {len(searches)} room searches.")
    return searches


def save_run_log_to_firebase(successful: bool, error: str=None, proxy: str=None):
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


def save_search_args(phone_number: str, room_counts: [int] = None, only_exterior: bool=None, max_price:int=None, name:str = None, is_active=None, is_authorized=None):
    doc_ref = args_collection.document(phone_number)
    search_doc = doc_ref.get()
    if search_doc.exists:
        search_data = search_doc.to_dict()
        search = RoomSearch.from_dict(search_data)
    else:
        search = RoomSearch(phones=[phone_number])

    if room_counts  is not None:
        search.num_rooms = room_counts
    if only_exterior is not None:
        search.only_exterior = only_exterior
    if max_price  is not None:
        print("need to set max price up")
    if name  is not None:
        search.name = name
    if is_active is not None:
        search.is_active = is_active
    if is_authorized is not None:
        search.is_authorized = is_authorized
    search_export = search.to_dict()
    doc_ref.set(search_export)
    return search


def save_search(phone_number: str, search: RoomSearch):
    doc_ref = args_collection.document(phone_number)
    search_dict = search.to_dict()
    doc_ref.set(search_dict)


def get_search(phone_number: str):
    doc_ref = args_collection.document(phone_number)
    search_doc = doc_ref.get()
    if search_doc.exists:
        search_data = search_doc.to_dict()
        search = RoomSearch.from_dict(search_data)
        return search
    else:
        return None


def delete_search(phone_number: str):
    doc_ref = args_collection.document(phone_number)
    doc_ref.delete()


def reset_search(phone_number: str):
    search = get_search(phone_number)
    if not search:
        return
    search.num_rooms = []
    search.only_exterior = False
    save_search(phone_number, search)
    return search

def save_before_and_after(before: list[Unit], after_removed: set[Unit], after_added: set[Unit], after_changed: set[Unit]):
    print("saving before and after")
    try:
        doc_name = datetime.now().isoformat()
        doc_ref = unit_change_collection.document(doc_name)
        before_sorted = sorted(before)
        doc_data = {
            "timestamp": datetime.now().isoformat(),
            "before_all": [x.to_dict() for x in before_sorted],
            "after_removed": [x.to_dict() for x in sorted(list(after_removed))],
            "after_added": [x.to_dict() for x in sorted(list(after_added))],
            "after_changed": [x.to_dict() for x in sorted(list(after_changed))]
        }
        doc_ref.set(doc_data)
        print(f"saved before and after: {doc_name}")
    except Exception as e:
        print(f"Failed to save before and after: {e}")

#
#
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
