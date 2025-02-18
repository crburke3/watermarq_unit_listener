from datetime import datetime
import json

import helpers
from classes.Unit import Unit


old_units_json = "/tmp/old_units.json"


def load_units_from_json():
    file_path = old_units_json
    try:
        # Open and load the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract the last updated timestamp and the list of units
        last_updated = data.get('last_updated', None)
        parsed_datetime = datetime.fromisoformat(last_updated)
        units_data = data.get('units', [])

        # Convert the JSON data to Unit objects
        units = [Unit.from_json(unit) for unit in units_data]
        for unit in units:
            helpers.add_csv_data(unit)
        return parsed_datetime, set(units)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None, set()
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from the file '{file_path}'.")
        return None, set()


def save_units_to_json(units):
    file_path = old_units_json
    last_updated = datetime.utcnow().isoformat()  # ISO 8601 format
    data = {
        'last_updated': last_updated,
        'units': [unit.to_dict() for unit in units]
    }

    # Save the data to the JSON file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

