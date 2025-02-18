import helpers
import main
from classes.RoomSearch import RoomSearch
from classes.Unit import Unit
from firebase_admin import firestore
import firebase_storing


firebase_db_path = "/old_units"
db = firestore.client()
last_successful_time, options = firebase_storing.load_units_from_firebase()
target_datetime = last_successful_time  # Replace with your timestamp
search_doc, doc_name = firebase_storing.find_closest_run_log(target_datetime)
ref = db.collection("watermarq_system").document("search_changes_main").collection("search_changes").document(doc_name)
doc = ref.get()

proxy_url = helpers.get_random_proxy_url()
main.run_watermarq_messaging(None, proxy_url=proxy_url)

if not doc.exists:
    print(f"Error: No data found at {firebase_db_path}.")
    exit(0)
# Extract last updated timestamp and units
data = doc.to_dict()

before_all = [Unit.from_json(x) for x in data['before_all']]
after_time, after_all = firebase_storing.load_units_from_firebase()

removed_units, added_units, price_changed_units, price_changed_units_data = helpers.compare_units(set(before_all),
                                                                                                  set(after_all))

for old_unit in before_all:
    has_same = False
    for new_unit in after_all:
        same_unit = old_unit == new_unit
        # print(f"comparing before: {old_unit.unit_number} | {new_unit.unit_number} same: {same_unit}")
        if (same_unit):
            print(f"Same unit: {old_unit.unit_number} | {new_unit.unit_number}")
            print(f"old: {old_unit}")
            print(f"new: {new_unit}")
            has_same = True
    if not has_same:
        print("NO SAME UNIT FOUND")
    print("....")
    print("....")

searches: [RoomSearch] = firebase_storing.load_room_searches()
for search in searches:
    search_removed_units, search_added_units, search_price_changed_units = helpers.filter_units_for_search(search,
                                                                                                           removed_units,
                                                                                                           added_units,
                                                                                                           price_changed_units)
    if len(search_removed_units) == 0 and len(search_added_units) == 0 and len(search_price_changed_units) == 0:
        print(f"no changes for search {search.name}")
        continue
    message = helpers.generate_message(search, search_removed_units, search_added_units, search_price_changed_units,
                                       price_changed_units_data)
    print(message)