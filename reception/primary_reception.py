import comms_help
import firebase_storing
from enum import Enum
import re
import helpers
import time

from Unit import Unit

SECRET_MESSAGE = 'thxchristian'


class MessageType(Enum):
    SUBSCRIBE='SUBSCRIBE'
    ROOM_COUNT='ROOM_COUNT'
    ONLY_EXTERIOR='ONLY_EXTERIOR'
    UNKNOWN="UNKNOWN"
    UNSUBSCRIBE="UNSUBSCRIBE"
    RESTART="RESTART"
    BUILDING="BUILDING"
    SECRET_MESSAGE="SECRET_MESSAGE"
    UNIT_INTEREST="UNIT_INTEREST"


def find_message_type(message: str):
    lower_message = message.lower()
    stripped_msg = lower_message.replace(' ', "")
    if stripped_msg in ['subscribe', 'start']:
        return MessageType.SUBSCRIBE
    if stripped_msg in ['unsubscribe', 'end']:
        return MessageType.UNSUBSCRIBE
    if stripped_msg == 'restart':
        return MessageType.RESTART
    if stripped_msg == "building":
        return MessageType.BUILDING
    if stripped_msg in ["thxchristian", "fuckyou"]:
        return MessageType.SECRET_MESSAGE

    room_count_pattern = r'^\d+(\s*,\s*\d+)*$'
    is_room_count = bool(re.match(room_count_pattern, stripped_msg))
    if is_room_count:
        return MessageType.ROOM_COUNT

    unit_number_pattern = r"^\d{3}$"
    is_unit_number = bool(re.match(unit_number_pattern, stripped_msg))
    if is_unit_number:
        return MessageType.UNIT_INTEREST

    if stripped_msg in ['yes', 'no']:
        return MessageType.ONLY_EXTERIOR

    return MessageType.UNKNOWN


def handle_subscription(from_number: str):
    existing_search = firebase_storing.get_search(from_number)
    response = "So you've heard about me 👀\n\n"
    response += "I'm here to let you know when rooms open up, are removed or have their price updated\n\n"
    response += "Standard text and mms rates apply 💅\n\n"
    if not existing_search:
        response += "Thank's for your interest 🙇 you've been added to the waitlist\n\n"
        response += "If you know the secret code, send it in your next text\n\n"
        response += "Otherwise, please wait for a text coming in the next few days/weeks\n\n"
        response += "You can always text 'unsubscribe' to opt out - no worries G"
        firebase_storing.save_search_args(from_number, is_active=False)
    else:
        response += "You can always text 'unsubscribe' to opt out - no worries G\n\n"
        response += "Look's like you're already registered, so lets get to it.\n\n"
        response += "Don't forget to put Christian Burke on your application if you end up signing \n\n"
        response += 'How many rooms are you looking for? (1...3)\n\n'
        response += 'Ex: 1\n'
        response += "Ex: 2,3"
        existing_search.is_authorized = True
        existing_search.is_active = True
    return response


def handle_secret_code(from_number: str, message: str):
    stripped_msg = message.replace(' ', "")
    if SECRET_MESSAGE in stripped_msg:
        response = "Congratulations you're in 😎\n\n"
        response += "Don't forget to put Christian Burke on your application if you end up signing \n\n"
        response += 'How many rooms are you looking for? (1...3)\n\n'
        response += 'Ex: 1\n'
        response += "Ex: 1,2,3"
        firebase_storing.save_search_args(from_number, is_active=True, is_authorized=True)
    else:
        response = "Incorrect secret code :( I bet you're cool though :*"
    return response


def handle_room_count(from_number: str, message: str):
    stripped_msg = message.replace(' ', "")
    room_counts_raw = stripped_msg.split(',')
    nums = [int(room_count) for room_count in room_counts_raw if room_count in ['1','2','3']]
    assert len(nums) > 0, "No recognized numbers, please try again EX: 1,2,3"
    firebase_storing.save_search_args(from_number, room_counts=nums)
    response = "Solid, do you only want to search for exterior facing rooms?\n\n"
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
    sublease_updated, sublease_units = firebase_storing.load_units_from_firebase(sublease=True)
    for sublease in sublease_units:
        all_units.append(sublease)
    good_units = helpers.filter_units(search, units=all_units)
    print(f"found {len(good_units)} for search: {from_number}")
    if len(good_units) == 0:
        initial_message = 'Well it looks like theres no units currently available with that criteria :/ \n'
        initial_message += 'But dont worry, i search every hour and will let you know when something is available\n\n'
        initial_message += 'You can always text "RESTART" to change your search criteria'
        return initial_message
    else:
        initial_message = helpers.generate_initial_search_message(search, good_units)
        return initial_message


def handle_unsubscribe(from_number: str):
    existing_search = firebase_storing.get_search(from_number)
    if existing_search:
        existing_search.is_active = False
        firebase_storing.save_search(from_number, existing_search)
    response = "I wont text you anymore, if you want to jump back in just send 'Subscribe'"
    return response


def handle_restart(from_number: str):
    firebase_storing.reset_search(from_number)
    response = "alrighty I cleared your prev search, text 'Subscribe' to start again"
    return response


def handle_building(from_number: str):
    img_url = "https://storage.googleapis.com/public-random/watermarq_map.png"
    message = "heres the building's map"
    comms_help.send_image(from_number, message, img_url)
    return "sending you the map..."


def handle_unit_interest(from_number: str, unit_number: str):
    last_updated, website_units = firebase_storing.load_units_from_firebase()
    sublease_updated, sublease_units = firebase_storing.load_units_from_firebase(sublease=True)
    website_unit = helpers.find_unit(website_units, unit_number)
    sublease_unit = helpers.find_unit(sublease_units, unit_number)
    if not website_unit and not sublease_unit:
        message = "I don't have any information on that unit 😞\n"
        message += "Its either been removed from the webiste/sublease list or was never there"
        return message
    firebase_storing.save_unit_interest(from_number=from_number, unit_number=unit_number)
    if website_unit:
        message = "This unit is being leased by Water Marq 👔\n"
        message += "You can apply to live here on the Water Marq webiste:\n"
        message += "https://www.watermarqaustin.com/floor-plans\n\n"
        message += "⚠️ To keep this service alive - PLEASE add 'Christian Burke' as the referral on your application ⚠️"
        return message
    if sublease_unit:
        assert isinstance(sublease_unit, Unit)
        assert sublease_unit.is_sublease
        message = "This unit is being subleased 🤝\n\n"
        message += f"You'll need to contact {sublease_unit.sublease_owner_name}\n"
        message += f"{sublease_unit.sublease_owner_phone}\n\n"
        message += "⚠️ To keep this service alive - PLEASE let them know 'Christian Burke' sent you ⚠️"
        if sublease_unit.sublease_owner_phone:
            subleaser_message = f"Someone is interested in your unit: {sublease_unit.unit_number} 👀"
            comms_help.send_message(sublease_unit.sublease_owner_phone, subleaser_message)
        return message


def handle_reception(from_number: str, raw_message: str):
    print(f"[TEXT:Recieved] {from_number} | {raw_message}")
    comms_help.send_telegram_message("", f"RECIEVED|{from_number}: {raw_message}")
    message = raw_message.lower()
    stripped_msg = message.replace(' ', "")
    message_type = find_message_type(message)
    response = "I don't know that one :( Plz try again"
    if message_type == MessageType.SUBSCRIBE:
        response = handle_subscription(from_number)
        comms_help.send_message(from_number, response)
        return response
    if message_type == MessageType.SECRET_MESSAGE:
        response = handle_secret_code(from_number, message)
        comms_help.send_message(from_number, response)
        return response
    if message_type == MessageType.UNSUBSCRIBE:
        response = handle_unsubscribe(from_number)
        comms_help.send_message(from_number, response)
        return response
    if message_type == MessageType.RESTART:
        response = handle_restart(from_number)
        comms_help.send_message(from_number, response)
        return response
    if message_type == MessageType.UNIT_INTEREST:
        response = handle_unit_interest(from_number=from_number, unit_number=stripped_msg)
        comms_help.send_message(from_number, response)
        return response

    search = firebase_storing.get_search(from_number)
    if search:
        if search.is_authorized:
            if message_type == MessageType.BUILDING:
                response = handle_building(from_number)
            if message_type == MessageType.ROOM_COUNT:
                response = handle_room_count(from_number, message)
            if message_type == MessageType.ONLY_EXTERIOR:
                response = handle_only_exterior(from_number, message)
                # comms_help.send_message(from_number, response)
                # time.sleep(1)
                response = handle_initial_search(from_number)
                comms_help.send_message(from_number, response)
                response = "oh yeah you can text 'building' and ill text you a picture of the room map\n"
                response += "text 'restart' if you want to change your search criteria\n\n"
                response += "also any venmo donations would be appreciated <3 \n\n"
                response += "https://account.venmo.com/u/Christian-Burke-6"
            comms_help.send_message(from_number, response)
        else:
            response = "I know that one, but you're still on the waitlist :("
            comms_help.send_message(from_number, response)
    else:
        response = "Not sure how you're seeing this. plz try sending 'subscribe'"
        comms_help.send_message(from_number, response)
    return response
