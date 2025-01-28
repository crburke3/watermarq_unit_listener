import os
os.environ["is_dev"] = "true"
import admin_functions
import comms_help
import firebase_storing
import helpers
import main
import sublease_handling
from reception import primary_reception

phone = '+17048062009'


def test_main():
    proxy_url = helpers.get_random_proxy_url()
    main.run_watermarq_messaging(None, proxy_url=proxy_url)


def test_add_sublease_unit():
    new_unit = sublease_handling.add_sublease_unit(
        unit_number="261",
        price="$6,969",
        floor_plan_type="2R two Bedrooms 1 Baths 712 sq.ft.",
        subleaser_name="test",
        subleaser_phone_number="+17048062009",
        availability_date="1/1/2030",
        notes="This is a test, its a townhome"
    )
    print(new_unit, new_unit.num_rooms())


def test_remove_sublease_unit():
    sublease_handling.remove_sublease_unit(unit_number="222")


def test_subscribe_response():
    message = "Subscribe"
    resp = primary_reception.handle_reception(phone, message)
    print(resp)


def test_secret_message_wrong():
    message = "shit"
    resp = primary_reception.handle_reception(phone, message)
    print(resp)


def test_secret_message_correct():
    message = "thxchristian"
    resp = primary_reception.handle_reception(phone, message)
    print(resp)


def test_room_number_response_single():
    message = '1'
    message_type = primary_reception.find_message_type(message)
    assert message_type == primary_reception.MessageType.ROOM_COUNT
    resp = primary_reception.handle_reception(phone, message)


def test_room_number_response_multiple():
    message = '2,3'
    message_type = primary_reception.find_message_type(message)
    assert message_type == primary_reception.MessageType.ROOM_COUNT
    resp = primary_reception.handle_reception(phone, message)


def test_only_exterior_true():
    message = 'yes'
    message_type = primary_reception.find_message_type(message)
    assert message_type == primary_reception.MessageType.ONLY_EXTERIOR
    resp = primary_reception.handle_reception(phone, message)


def test_only_exterior_false():
    message = 'no'
    message_type = primary_reception.find_message_type(message)
    assert message_type == primary_reception.MessageType.ONLY_EXTERIOR
    resp = primary_reception.handle_reception(phone, message)


def test_restart():
    message = 'RESTART'
    message_type = primary_reception.find_message_type(message)
    assert message_type == primary_reception.MessageType.RESTART
    resp = primary_reception.handle_reception(phone, message)


def test_mms():
    comms_help.send_image(phone, "WOO22", "https://storage.googleapis.com/public-random/watermarq_map.png")


def test_building():
    message = 'BUILDING'
    message_type = primary_reception.find_message_type(message)
    assert message_type == primary_reception.MessageType. BUILDING
    resp = primary_reception.handle_reception(phone, message)


def test_send_manual_message():
    message = "Subscribe"
    number = "+16106756886"
    resp = primary_reception.handle_reception(number, message)


def test_initial_search():
    from_number = "+17048062009"
    message = primary_reception.handle_initial_search(from_number)
    print(message)


def test_unit_interest():
    unit_number = "261"
    message = primary_reception.handle_unit_interest("+17048062009", unit_number)
    print(message)


def test_send_message_to_all_subscribers():
    message = "This is christian here 😼, I've updated the system 🐱‍💻\n\n"
    message += "You can now sublease your apt through this system 😈\n"
    message += "I'll be adding a way to do this through texting in here, but for now you need to text me personally.\n"
    message += "Text the following info my personal number: 704-806-2009\n\n"
    message += " - Unit number\n"
    message += " - Floor plan ex: 1F One Bedroom 1 Bath 706 - 788 sq.ft.\n"
    message += " - Your Price\n"
    message += " - When the unit will start being available ex: 1/20/2025\n"
    message += " - Your Name or psuedonym\n"
    message += " - Any notes you'd like included\n"
    message += " - How you'd like to be contacted (your email or your phone number)\n\n"
    message += "By sending me this info, you agree that this system can share your name/psuedonym and contact info with anyone who expresses interest in your unit. " \
               "Any user will be able to text this service to recieve your contact info in regards to subleasing your apt. " \
               "Currently there are 23 people signed up for this system 🎉.\n\n" \
               "Oh also, the system will text you whenever someone expressed interest 👀.\n"
    message += "Your subleased unit will show up in the search results like this (subject to change): \n\n"
    message += "• 261 | $6,969\n"
    message += "  Sublease 🤝\n"
    message += "  Townhome 🏠\n"
    message += "  2R two Bedrooms 1 Baths 712 sq.ft.\n"
    message += "  Availability: 1/1/2030\n"
    message += "  Num Rooms: 2\n"
    message += "  Exterior Facing 🪟\n"
    message += "  View Facing: Townhome 🏘️\n"
    message += "  Notes: It totally wasn't me who broke the bedroom window\n"

    searches = firebase_storing.load_room_searches()
    for search in searches:
        for user_phone in search.phones:
            comms_help.send_text(user_phone, message)


def test_activate_search():
    admin_functions.activate_search("+17048062009")
