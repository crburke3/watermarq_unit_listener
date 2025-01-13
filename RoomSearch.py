from typing import List

class RoomSearch:
    def __init__(self, name: str, phones: List[str], num_rooms: List[int], only_exterior: bool):
        self.name = name
        self.phones = phones
        self.num_rooms = num_rooms
        self.only_exterior = only_exterior

    def __repr__(self):
        return f"RoomSearch(name={self.name}, phones={self.phones}, num_rooms={self.num_rooms})"
