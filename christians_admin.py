import admin_functions
import firebase_storing

searches = firebase_storing.load_room_searches()
inactive_searches = [x for x in searches if x.is_authorized == False]

for search in inactive_searches:
    phone = search.phones[0]
    admin_functions.activate_search(phone)





