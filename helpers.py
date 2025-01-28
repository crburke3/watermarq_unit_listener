import csv
from datetime import datetime

import pytz

from RoomSearch import RoomSearch
from Unit import Unit
from typing import Set
import random


def compare_units(existing_units: Set[Unit], new_units: Set[Unit]):
    # Units that exist in existing_units but not in new_units (removed from the web)
    removed_units = {unit for unit in existing_units if unit not in new_units}

    # Units that exist in new_units but not in existing_units (new on the web)
    added_units = {unit for unit in new_units if unit not in existing_units}

    # Units whose prices differ locally and on the web
    price_changed_units_set = {
        unit for unit in existing_units
        if unit in new_units and unit.price != next(u.price for u in new_units if u == unit)
    }
    old_units_dict = {unit.unit_number: unit for unit in existing_units}
    new_units_dict = {unit.unit_number: unit for unit in new_units}
    price_changed_units = []
    for unit_number, new_unit in new_units_dict.items():
        old_unit = old_units_dict.get(unit_number)
        if old_unit and old_unit.price != new_unit.price:
            change = "increased" if new_unit.price > old_unit.price else "decreased"
            price_changed_units.append((
                new_unit,
                old_unit.price,
                new_unit.price,
                change
            ))

    return removed_units, added_units, price_changed_units_set, price_changed_units


def find_unit(units: [Unit], unit_number: str):
    return next((u for u in units if u.unit_number == unit_number), None)

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


def filter_units(search: RoomSearch, units: [Unit]):
    search_units = set(filter(lambda unit: unit.num_rooms() in search.num_rooms, units))
    ret_units = set()
    if search.only_exterior:
        for unit in search_units:
            if unit.is_exterior_facing:
                ret_units.add(unit)
                continue
            if unit.notes:
                if 'townhome' in unit.notes.lower():
                    ret_units.add(unit)
                    continue
    else:
        ret_units = search_units
    sorted_units = sorted(list(ret_units))
    return sorted_units


def filter_units_for_search(search: RoomSearch, removed_units, added_units, price_changed_units):
    search_removed_units = set()
    search_added_units = set()
    search_price_changed_units = set()
    for idx, section in enumerate([removed_units, added_units, price_changed_units]):
        ### Actual filtering
        search_units = set(filter_units(search, section))
        if idx == 0: search_removed_units = search_units
        if idx == 1: search_added_units = search_units
        if idx == 2: search_price_changed_units = search_units
    return search_removed_units, search_added_units, search_price_changed_units


def generate_initial_search_message(search: RoomSearch, units: [Unit]):
    sorted_units = sorted(list(units))
    message = "Here's the units that are currently available in your search\n"
    message += "I'll text you whenever one with your criteria is added, removed or updated 😘\n\n"
    message += "\n".join(f"• {unit_description(obj)}" for obj in sorted_units)
    return message


def generate_message(search: RoomSearch, removed_units, added_units, price_changed_units, price_changed_units_data, sublease=False):
    removed_list = sorted(list(removed_units))
    added_list = sorted(list(added_units))
    price_changed = sorted(list(price_changed_units))
    message = f"We've got a watermarq room update 👀\n"
    if len(removed_units) > 0:
        if sublease:
            message += "the follow units are no longer available for sublease 😥\n\n"
        else:
            message += "the following units have been removed from water marq's website 😥\n\n"
        message += "\n".join(f"• {unit_description(obj)}" for obj in removed_list)
        message += "\n"

    if len(added_units) > 0:
        if sublease:
            message += "the following units are now available for sublease 👏\n\n"
        else:
            message += "the following units have been added to watermarqs website 👏\n\n"
        message += "\n".join(f"• {unit_description(obj)}" for obj in added_list)
        message += "\n"

    if len(price_changed_units) > 0:
        message += "the following units have had their prices changed 🤔\n\n"
        for price_unit in price_changed:
            message += f"• {unit_description(price_unit)}"
            price_change_item = None
            for item in price_changed_units_data:
                if item[0] == price_unit:
                    price_change_item = item
                    break
            if price_change_item:
                # message += f"  old price: {price_change_item[1]}\n"
                message += f"  new price: {price_change_item[2]}"
                dec_or_inc = price_change_item[3]
                if dec_or_inc == 'increased':
                    message += "🔺\n"
                else:
                    message += "💚\n"
            message += "\n"
        message += "\n"

    if sublease:
        message += "If you're interested in a sublease, text the unit number and I'll send you their contact info"

    return message


def unit_description(unit: Unit):
    desc = f"{unit.unit_number} | {unit.price}\n"
    desc += f"  Sublease 🤝\n" if unit.is_sublease else ""
    desc += f"  Townhome 🏠\n" if unit.is_townhome() else ""
    desc += f"  {unit.floor_plan_type}\n"
    desc += f"  Availability: {unit.availability_date}\n"
    desc += f"  Num Rooms: {unit.num_rooms()}\n" if unit.floor_plan_type else ""
    desc += f"  Exterior Facing 🪟\n" if unit.is_exterior_facing else "  Not exterior facing"
    desc += f"  Corner Unit 🥇\n" if unit.corner_type else ""
    desc += f"  View Ranking: {int(unit.view_rank) * '⭐'}\n" if unit.view_rank else ""
    desc += f"  View Facing: {unit.primary_exterior_face} {view_emoji(unit)}\n" if unit.primary_exterior_face else ""
    desc += f"  Notes: {unit.notes}\n" if unit.notes else ""
    return desc


def view_emoji(unit: Unit):
    view = unit.primary_exterior_face.lower()
    if view == 'townhome': return '🏘️'
    if view == 'street': return '🚥'
    if view == 'pool': return '🏊'
    if view == 'parking lot': return '🚗'
    return ''


def get_current_cst_date():
    cst = pytz.timezone('US/Central')
    current_time_cst = datetime.now(cst)
    # Format the date as "12 January 2025"
    formatted_date = current_time_cst.strftime("%d %B %Y")
    return formatted_date


def load_proxy_list() -> [str]:
    return [
    "brd-customer-hl_ceb3d9f9-zone-datacenter_proxy1-ip-158.46.166.29:a9iprakm5w98@brd.superproxy.io:33335",
    "brd-customer-hl_ceb3d9f9-zone-datacenter_proxy1-ip-158.46.169.117:a9iprakm5w98@brd.superproxy.io:33335",
    "brd-customer-hl_ceb3d9f9-zone-datacenter_proxy1-ip-178.171.58.92:a9iprakm5w98@brd.superproxy.io:33335",
    "brd-customer-hl_ceb3d9f9-zone-datacenter_proxy1-ip-178.171.58.97:a9iprakm5w98@brd.superproxy.io:33335",
    "brd-customer-hl_ceb3d9f9-zone-datacenter_proxy1-ip-178.171.117.112:a9iprakm5w98@brd.superproxy.io:33335",
    "brd-customer-hl_ceb3d9f9-zone-datacenter_proxy1-ip-178.171.117.113:a9iprakm5w98@brd.superproxy.io:33335",
    "brd-customer-hl_ceb3d9f9-zone-datacenter_proxy1-ip-178.171.117.116:a9iprakm5w98@brd.superproxy.io:33335",
    "brd-customer-hl_ceb3d9f9-zone-datacenter_proxy1-ip-178.171.117.117:a9iprakm5w98@brd.superproxy.io:33335",
    "brd-customer-hl_ceb3d9f9-zone-datacenter_proxy1-ip-178.171.117.118:a9iprakm5w98@brd.superproxy.io:33335",
    "brd-customer-hl_ceb3d9f9-zone-datacenter_proxy1-ip-158.46.167.209:a9iprakm5w98@brd.superproxy.io:33335",
    "brd-customer-hl_ceb3d9f9-zone-datacenter_proxy1-ip-158.46.170.107:a9iprakm5w98@brd.superproxy.io:33335",
    "brd-customer-hl_ceb3d9f9-zone-datacenter_proxy1-ip-178.171.90.37:a9iprakm5w98@brd.superproxy.io:33335",
    "brd-customer-hl_ceb3d9f9-zone-datacenter_proxy1-ip-178.171.58.170:a9iprakm5w98@brd.superproxy.io:33335",
    "brd-customer-hl_ceb3d9f9-zone-datacenter_proxy1-ip-178.171.58.211:a9iprakm5w98@brd.superproxy.io:33335",
    "brd-customer-hl_ceb3d9f9-zone-datacenter_proxy1-ip-178.171.116.13:a9iprakm5w98@brd.superproxy.io:3333"
  ]

def get_random_proxy_url():
    proxies = load_proxy_list()
    proxy_to_use = random.choice(proxies)
    proxy_url = f"http://{proxy_to_use}"
    return proxy_url