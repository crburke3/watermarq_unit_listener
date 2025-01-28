from typing import List, Dict


class UnitInterest:
    def __init__(self, unit_number: str, interest_count: int):
        self.unit_number = unit_number
        self.interest_count = interest_count

    def __repr__(self):
        return f"{self.unit_number} | {self.interest_count}"


class RoomSearch:
    def __init__(self, phones: List[str], name: str = None, num_rooms: List[int] = None,
                 only_exterior: bool = None, is_active=True, interested_units: List[UnitInterest] = None):
        self.name = name
        self.phones = phones
        self.num_rooms = num_rooms
        self.only_exterior = only_exterior
        self.is_active = is_active
        self.interested_units = interested_units if interested_units is not None else []

    def __repr__(self):
        return (f"RoomSearch(name={self.name}, phones={self.phones}, num_rooms={self.num_rooms}, "
                f"only_exterior={self.only_exterior}, interested_units={self.interested_units}) "
                f"active: {self.is_active}")

    @classmethod
    def from_dict(cls, data: Dict) -> 'RoomSearch':
        """
        Create a RoomSearch instance from a dictionary.
        """
        interested_units = [
            UnitInterest(unit['unit_number'], unit['interest_count'])
            for unit in data.get('interested_units', [])
        ]
        return cls(
            name=data['name'],
            phones=data['phones'],
            num_rooms=data['num_rooms'],
            only_exterior=data['only_exterior'],
            is_active=data['is_active'],
            interested_units=interested_units
        )

    def to_dict(self) -> Dict:
        """
        Convert the RoomSearch instance to a dictionary.
        """
        return {
            'name': self.name,
            'phones': self.phones,
            'num_rooms': self.num_rooms,
            'only_exterior': self.only_exterior,
            'is_active': self.is_active,
            'interested_units': [
                {'unit_number': unit.unit_number, 'interest_count': unit.interest_count}
                for unit in self.interested_units
            ]
        }
