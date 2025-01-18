import comms_help
import firebase_storing
import helpers
import local_storing
import web_calls as wc
from RoomSearch import RoomSearch
from Unit import Unit
from typing import Set
from datetime import datetime


MIN_SECS_BETWEEN_RUNS = 1


def run_watermarq_messaging(args):
    # Load existing units from local storage
    searches: [RoomSearch] = firebase_storing.load_room_searches()
    if len(searches) == 0:
        print("skipping room search cause no active searches")
        return {"message": "no room searches, skipping scraping"}, 200
    last_updated, existing_units = firebase_storing.load_units_from_firebase()
    curr_time = datetime.utcnow()
    if last_updated:
        seconds_since_last_run = (curr_time - last_updated).total_seconds()
        # if seconds_since_last_run < MIN_SECS_BETWEEN_RUNS:
            # print(f"Skipping run, too soon. {seconds_since_last_run} seconds between")
            # return {}, 201
    else:
        print("No unit json file, assuming first time running.")

    # Load the current available units from the web
    new_units: Set[Unit] = set()
    floor_plans = wc.getAvailableFloorplans()
    if len(floor_plans) == 0:
        raise Exception('Could not find any floorplans from availableFloorPlans function')
    for floor_plan in floor_plans:
        print(f"Getting available units for floorPlan: {floor_plan.name}...", end="", flush=True)
        move_in_date = helpers.get_current_cst_date()
        currently_available_units: Set[Unit] = wc.getUnitListByFloor(floorPlan=floor_plan, moveinDate=move_in_date)
        print(f"  {currently_available_units} available")
        new_units.update(currently_available_units)

    # Compare the existing units with the new units
    removed_units, added_units, price_changed_units = helpers.compare_units(existing_units, new_units)

    # Print the results
    print(f"Units removed from the web: {removed_units}")
    print(f"Units added to the web: {added_units}")
    print(f"Units with price differences: {price_changed_units}")


    for search in searches:
        search_removed_units, search_added_units, search_price_changed_units = helpers.filter_units_for_search(search, removed_units, added_units, price_changed_units)
        if len(search_removed_units) == 0 and len(search_added_units) == 0 and len(search_price_changed_units) == 0:
            print(f"no changes for search {search.name}")
            continue
        message = helpers.generate_message(search, search_removed_units, search_added_units, search_price_changed_units)
        print(f"sending message to {search.name}")
        comms_help.send_telegram_message("", message)
        for phone in search.phones:
            comms_help.send_text(phone, message)

    firebase_storing.save_units_to_firebase(new_units)
    return {"message": "successful scrapage"}, 200
