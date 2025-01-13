import csv
from datetime import datetime

import pytz

from RoomSearch import RoomSearch
from Unit import Unit
from typing import Set


def compare_units(existing_units: Set[Unit], new_units: Set[Unit]):
    # Units that exist in existing_units but not in new_units (removed from the web)
    removed_units = {unit for unit in existing_units if unit not in new_units}

    # Units that exist in new_units but not in existing_units (new on the web)
    added_units = {unit for unit in new_units if unit not in existing_units}

    # Units whose prices differ locally and on the web
    price_changed_units = {
        unit for unit in existing_units
        if unit in new_units and unit.price != next(u.price for u in new_units if u == unit)
    }

    return removed_units, added_units, price_changed_units



def load_unit_csv():
    csv_file_path = "watermark_units.csv"
    units = []

    # Open the CSV file and read it
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        # Iterate over each row in the CSV
        for row in csv_reader:
            unit = Unit.from_json(row)
            units.append(unit)
    return set(units)


csv_units = load_unit_csv()


def add_csv_data(unit):
    for csv_unit in csv_units:
        if unit.unit_number == csv_unit.unit_number:
            unit.is_exterior_facing = csv_unit.is_exterior_facing
            unit.primary_exterior_face = csv_unit.primary_exterior_face
            unit.is_corner_unit = csv_unit.is_corner_unit
            unit.corner_type = csv_unit.corner_type
            unit.size_rank = csv_unit.size_rank
            unit.view_rank = csv_unit.view_rank
            unit.notes = csv_unit.notes
            unit.floor_plan_type = csv_unit.floor_plan_type


def filter_units_for_search(search: RoomSearch, removed_units, added_units, price_changed_units):
    search_removed_units = set()
    search_added_units = set()
    search_price_changed_units = set()
    for idx, section in enumerate([removed_units, added_units, price_changed_units]):
        ### Actual filtering
        search_units = set(filter(lambda unit: unit.num_rooms() in search.num_rooms, section))
        if search.only_exterior:
            search_units = set(filter(lambda unit: unit.is_exterior_facing, search_units))

        if idx == 0: search_removed_units = search_units
        if idx == 1: search_added_units = search_units
        if idx == 2: search_price_changed_units = search_units
    return search_removed_units, search_added_units, search_price_changed_units


def generate_message(search: RoomSearch, removed_units, added_units, price_changed_units):
    removed_list = sorted(list(removed_units))
    added_list = sorted(list(added_units))
    price_changed = sorted(list(price_changed_units))
    message = f"Hey {search.name}. We've got a watermarq room update 👀\n"
    if len(removed_units) > 0:
        message += "the following units have been removed from watermarqs website 😥\n"
        message += "\n".join(f"• {unit_description(obj)}" for obj in removed_list)
        message += "\n"

    if len(added_units) > 0:
        message += "the following units have been added to watermarqs website 👏\n"
        message += "\n".join(f"• {unit_description(obj)}" for obj in added_list)
        message += "\n"

    if len(price_changed_units) > 0:
        message += "the following units have had their prices changed 🤔\n"
        message += "\n:".join(f"• {unit_description(obj)}" for obj in price_changed)
        message += "\n"

    return message


def unit_description(unit: Unit):
    desc = f"{unit.unit_number} | {unit.price}\n"
    desc += f"  {unit.floor_plan_type}\n"
    desc += f"  Num Rooms: {unit.num_rooms()}\n" if unit.floor_plan_type else ""
    desc += f"  Exterior Facing 🪟\n" if unit.is_exterior_facing else ""
    desc += f"  Corner Unit 🥇\n" if unit.corner_type else ""
    desc += f"  View Ranking: {int(unit.view_rank) * '⭐'}\n" if unit.view_rank else ""
    desc += f"  View Facing: {unit.primary_exterior_face}" if unit.primary_exterior_face else ""
    desc += f"  {unit.notes}" if unit.notes else ""
    return desc


def get_current_cst_date():
    cst = pytz.timezone('US/Central')
    current_time_cst = datetime.now(cst)
    # Format the date as "12 January 2025"
    formatted_date = current_time_cst.strftime("%d %B %Y")
    return formatted_date
