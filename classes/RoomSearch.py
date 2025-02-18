from typing import List, Dict

class UnitInterest:
    def __init__(self, unit_number: str, interest_count: int):
        self.unit_number = unit_number
        self.interest_count = interest_count

    def __repr__(self):
        return f"{self.unit_number} | {self.interest_count}"

class RoomSearch:
    def __init__(self, phones: List[str], name: str = None, num_rooms: List[int] = None,
                 only_exterior: bool = None, is_active=True, interested_units: List[UnitInterest] = None,
                 is_authorized: bool = False, days_delay: int = 0, seconds_delay: int = 0):
        self.name = name
        self.phones = phones
        self.num_rooms = num_rooms
        self.only_exterior = only_exterior
        self.is_active = is_active
        self.interested_units = interested_units if interested_units is not None else []
        self.is_authorized = is_authorized
        self.days_delay = days_delay
        self.seconds_delay = seconds_delay

    def __repr__(self):
        auth_emoji = "✅" if self.is_authorized else "❌"
        active_emoji = "✅" if self.is_active else "❌"
        return f"{self.phones} | Auth: {auth_emoji} | Active: {active_emoji} | {self.num_rooms} | {self.only_exterior} | {self.interested_units} | Days Delay: {self.days_delay} | Seconds Delay: {self.seconds_delay}"

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
            interested_units=interested_units,
            is_authorized=data.get('is_authorized', False),
            days_delay=data.get('days_delay', 0),
            seconds_delay=data.get('seconds_delay', 0)
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
            'is_authorized': self.is_authorized,
            'interested_units': [
                {'unit_number': unit.unit_number, 'interest_count': unit.interest_count}
                for unit in self.interested_units
            ],
            'days_delay': self.days_delay,
            'seconds_delay': self.seconds_delay
        }