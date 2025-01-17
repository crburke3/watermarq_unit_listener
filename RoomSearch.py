from typing import List, Dict


class RoomSearch:
    def __init__(self,  phones: List[str], name: str=None, num_rooms: List[int] = None, only_exterior: bool = None):
        self.name = name
        self.phones = phones
        self.num_rooms = num_rooms
        self.only_exterior = only_exterior

    def __repr__(self):
        return f"RoomSearch(name={self.name}, phones={self.phones}, num_rooms={self.num_rooms}, only_exterior={self.only_exterior})"

    @classmethod
    def from_dict(cls, data: Dict) -> 'RoomSearch':
        """
        Create a RoomSearch instance from a dictionary.
        """
        return cls(
            name=data['name'],
            phones=data['phones'],
            num_rooms=data['num_rooms'],
            only_exterior=data['only_exterior']
        )

    def to_dict(self) -> Dict:
        """
        Convert the RoomSearch instance to a dictionary.
        """
        return {
            'name': self.name,
            'phones': self.phones,
            'num_rooms': self.num_rooms,
            'only_exterior': self.only_exterior
        }
