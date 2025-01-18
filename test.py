import comms_help
import main
from reception import primary_reception


phone = '+17048062009'


def test_main():
    main.run_watermarq_messaging(None)


def test_subscribe_response():
    message = "SUBSCRIBE"
    resp = primary_reception.handle_reception(phone, message)
    print(resp)


def test_secret_message_correct():
    message = "thxchristian"
    resp = primary_reception.handle_reception(phone, message)
    print(resp)


def test_secret_message_wrong():
    message = "fuckyou"
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
