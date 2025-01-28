import comms_help
import firebase_storing
import helpers
from RoomSearch import RoomSearch
from Unit import Unit


def add_sublease_unit(unit_number: str, subleaser_name: str, subleaser_phone_number: str, price: str, availability_date:str, floor_plan_type: str, notes: str = None) -> Unit:
    new_unit = Unit(
        unit_number=unit_number,
        price=price,
        notes=notes,
        availability_date=availability_date,
        is_sublease=True,
        sublease_owner_name=subleaser_name,
        sublease_owner_phone=subleaser_phone_number,
        floor_plan_type=floor_plan_type
    )
    helpers.add_csv_data(new_unit)
    new_unit.notes = notes
    last_updated, existing_units = firebase_storing.load_units_from_firebase(sublease=True)
    units_to_save = set(existing_units)
    if new_unit in units_to_save:
        units_to_save.remove(new_unit)
    units_to_save.add(new_unit)
    units_to_save = list(units_to_save)
    firebase_storing.save_units_to_firebase(units=units_to_save, sublease=True)
    searches: [RoomSearch] = firebase_storing.load_room_searches()
    removed_units = {}
    added_units = {new_unit}
    price_changed_units = {}
    price_changed_units_data = []
    for search in searches:
        search_removed_units, search_added_units, search_price_changed_units = helpers.filter_units_for_search(search, removed_units, added_units, price_changed_units)
        if len(search_removed_units) == 0 and len(search_added_units) == 0 and len(search_price_changed_units) == 0:
            continue
        message = helpers.generate_message(search, search_removed_units, search_added_units, search_price_changed_units, price_changed_units_data, sublease=True)
        comms_help.send_telegram_message("", message)
        for phone in search.phones:
            comms_help.send_text(phone, message)
    return new_unit


def remove_sublease_unit(unit_number: str):
    last_updated, existing_subleases = firebase_storing.load_units_from_firebase(sublease=True)
    unit = next((u for u in existing_subleases if u.unit_number == unit_number), None)
    if not unit:
        raise Exception(f"failed to find unit: {unit_number}")
    filtered_subleases = [x for x in existing_subleases if x.unit_number != unit_number]
    firebase_storing.save_units_to_firebase(units=filtered_subleases, sublease=True)
    searches: [RoomSearch] = firebase_storing.load_room_searches()
    removed_units = {unit}
    added_units = {}
    price_changed_units = {}
    price_changed_units_data = []
    for search in searches:
        search_removed_units, search_added_units, search_price_changed_units = helpers.filter_units_for_search(search, removed_units, added_units, price_changed_units)
        if len(search_removed_units) == 0 and len(search_added_units) == 0 and len(search_price_changed_units) == 0:
            continue
        message = helpers.generate_message(search, search_removed_units, search_added_units, search_price_changed_units, price_changed_units_data, sublease=True)
        comms_help.send_telegram_message("", message)
        for phone in search.phones:
            comms_help.send_text(phone, message)
