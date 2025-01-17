import comms_help
import firebase_storing
from enum import Enum
import re
import helpers

class MessageType(Enum):
    SUBSCRIBE='SUBSCRIBE'
    ROOM_COUNT='ROOM_COUNT'
    ONLY_EXTERIOR='ONLY_EXTERIOR'
    UNKNOWN="UNKNOWN"
    UNSUBSCRIBE="UNSUBSCRIBE"
    RESTART="RESTART"
    BUILDING="BUILDING"


def handle_subscription(from_number: str):
    response = "So you've heard about me 👀\n"
    response += "I'm here to let you know when rooms open up.\n"
    response += 'How many rooms are you looking for? (1...3)\n\n'
    response += 'Ex: 1\n'
    response += "Ex: 1,2,3\n"
    firebase_storing.save_search_args(from_number)
    return response


def find_message_type(message: str):
    lower_message = message.lower()
    stripped_msg = lower_message.replace(' ', "")
    if lower_message == 'subscribe':
        return MessageType.SUBSCRIBE
    if lower_message == 'unsubscribe':
        return MessageType.UNSUBSCRIBE
    if lower_message == 'restart':
        return MessageType.RESTART
    if lower_message == "building":
        return MessageType.BUILDING

    pattern = r'^\d+(\s*,\s*\d+)*$'
    is_room_count = bool(re.match(pattern, stripped_msg))
    if is_room_count:
        return MessageType.ROOM_COUNT

    if stripped_msg in ['yes', 'no']:
        return MessageType.ONLY_EXTERIOR

    return MessageType.UNKNOWN


def handle_room_count(from_number: str, message: str):
    stripped_msg = message.replace(' ', "")
    room_counts_raw = stripped_msg.split(',')
    nums = [int(room_count) for room_count in room_counts_raw if room_count in ['1','2','3']]
    assert len(nums) > 0, "No recognized numbers, please try again EX: 1,2,3"
    firebase_storing.save_search_args(from_number, room_counts=nums)
    response = "Solid, would do you only want to search for exterior facing rooms?\n\n"
    response += "(yes or no)"
    return response


def handle_only_exterior(from_number: str, message: str):
    if 'yes' in message:
        firebase_storing.save_search_args(from_number, only_exterior=True)
    elif 'no' in message:
        firebase_storing.save_search_args(from_number, only_exterior=False)
    else:
        raise Exception('Did not find "yes" or "no" please try again')
    response = "Tight. Let me search... "
    return response


def handle_initial_search(from_number: str):
    print(f"initial search for: {from_number}")
    search = firebase_storing.get_search(phone_number=from_number)
    if not search:
        raise Exception(f'could not find search for number: {from_number}')
    last_updated, all_units = firebase_storing.load_units_from_firebase()
    good_units = helpers.filter_units(search, units=all_units)
    if len(good_units) == 0:
        initial_message = 'Well it looks like theres no units currently available with that criteria :/ \n'
        initial_message += 'But dont worry, i search every hour and will let you know when something is available\n\n'
        initial_message += 'You can always text "RESTART" to change your search criteria'
        return initial_message
    else:
        initial_message = helpers.generate_initial_search_message(search, good_units)
    return initial_message


def handle_unsubscribe(from_number: str):
    firebase_storing.delete_search(from_number)
    response = "I wont text you anymore, if you want to jump back in just send SUBSCRIBE"
    return response


def handle_restart(from_number: str):
    firebase_storing.delete_search(from_number)
    response = "alrighty I cleared your prev search, text SUBSCRIBE to start again"
    return response


def handle_building(from_number: str):
    img_url = "https://storage.googleapis.com/public-random/watermarq_map.png"
    message = "heres the building's map"
    comms_help.send_image(from_number, message, img_url)


def handle_reception(from_number: str, raw_message: str):
    message = raw_message.lower()
    message_type = find_message_type(message)
    response = 'try again plz...'
    if message_type == MessageType.SUBSCRIBE:
        response = handle_subscription(from_number)
    if message_type == MessageType.UNSUBSCRIBE:
        response = handle_unsubscribe(from_number)
    if message_type == MessageType.RESTART:
        response = handle_restart(from_number)
    if message_type == MessageType.BUILDING:
        handle_building(from_number)
    if message_type == MessageType.ROOM_COUNT:
        response = handle_room_count(from_number, message)
    if message_type == MessageType.ONLY_EXTERIOR:
        response = handle_only_exterior(from_number, message)
        comms_help.send_message(from_number, response)
        response = handle_initial_search(from_number)
        comms_help.send_message(from_number, response)
        response = "oh yeah you can send the message 'BUILDING' and ill text you a picture of the room layouts"
    comms_help.send_message(from_number, response)
    return response
