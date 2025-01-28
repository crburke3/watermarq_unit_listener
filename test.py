import comms_help
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
