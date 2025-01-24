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
import firebase_storing


firebase_db_path = "/old_units"
db = firestore.client()
ref = db.collection("watermarq_system").document("search_changes_main").collection("search_changes").document("2025-01-24T13:00:24.878127")

doc = ref.get()

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