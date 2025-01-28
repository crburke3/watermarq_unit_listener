import comms_help
import firebase_storing


def activate_search(from_number: str):
    search = firebase_storing.get_search(from_number)
    assert search, f"Could not active search: {from_number} cause couldnt find the search"
    search.is_active = True
    search.is_authorized = True
    firebase_storing.save_search(from_number, search)
    message = "You're finally off the waitlist 🎉\n"
    message += "Remember you can always text 'unsubscribe' to opt out\n\n"
    message += "Don't forget to put Christian Burke on your application if you end up signing \n\n"
    message += 'How many rooms are you looking for? (1...3)\n\n'
    message += 'Ex: 1\n'
    message += "Ex: 1,2,3"
    comms_help.send_message(from_number, message)

