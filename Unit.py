class Unit:
    def __init__(self, unit_number, price=None, is_exterior_facing=None, primary_exterior_face=None,
                 is_corner_unit=None, corner_type=None, size_rank=None, view_rank=None, notes=None,
                 floor_plan_type=None, availability_date=None, is_sublease=None, sublease_owner_name=None, sublease_owner_phone=None):
        self.unit_number = unit_number
        self.price = price
        self.is_exterior_facing = is_exterior_facing
        self.primary_exterior_face = primary_exterior_face
        self.is_corner_unit = is_corner_unit
        self.corner_type = corner_type
        self.size_rank = size_rank
        self.view_rank = view_rank
        self.notes = notes
        self.floor_plan_type = floor_plan_type
        self.availability_date = availability_date  # new property
        self.is_sublease = is_sublease  # new property
        self.sublease_owner_name = sublease_owner_name  # new property
        self.sublease_owner_phone = sublease_owner_phone  # new property

    def num_rooms(self):
        if not self.floor_plan_type:
            print(f"could not find floor plan for: {self.unit_number}")
            return None
        plan_type = self.floor_plan_type.lower()
        if "studio" in plan_type:
            return 1
        if "one bedroom" in plan_type:
            return 1
        if "two bedroom" in plan_type:
            return 2
        if "three bedroom" in plan_type:
            return 3
        print(f"unknown floor plan for: {self.unit_number} | ${plan_type}")
        return None



    def __repr__(self):
        emojis = ""
        emojis += "🪟" if self.is_exterior_facing else ""
        emojis += "🥇" if self.is_corner_unit else ""
        emojis += "🏠" if self.is_townhome() else ""
        val = f"{self.unit_number}{emojis} {self.price}"
        val += f" {self.num_rooms()} rooms" if self.floor_plan_type else ""
        # if self.availability_date:
        #     val += f" Available on: {self.availability_date}"  # display availability date if present
        return val

    @classmethod
    def from_json(cls, json_data):
        return cls(
            unit_number=json_data['unit_number'],
            is_exterior_facing=json_data['is_exterior_facing'],
            primary_exterior_face=json_data['primary_exterior_face'],
            is_corner_unit=json_data['is_corner_unit'],
            corner_type=json_data['corner_type'],
            size_rank=json_data['size_rank'],
            view_rank=json_data['view_rank'],
            notes=json_data['notes'],
            price=json_data.get('price', None),
            floor_plan_type=json_data.get('floor_plan_type', None),
            availability_date=json_data.get('availability_date', None),
            is_sublease=json_data.get('is_sublease', None),
            sublease_owner_name=json_data.get('sublease_owner_name', None),
            sublease_owner_phone=json_data.get('sublease_owner_phone', None)
        )

    def is_townhome(self):
        if self.notes:
            if "townhome" in self.notes.lower():
                return True
        return False


    def to_dict(self):
        """
        Converts the Unit object into a dictionary for serialization.
        """
        return {
            'unit_number': self.unit_number,
            'price': self.price,
            'is_exterior_facing': self.is_exterior_facing,
            'primary_exterior_face': self.primary_exterior_face,
            'is_corner_unit': self.is_corner_unit,
            'corner_type': self.corner_type,
            'size_rank': self.size_rank,
            'view_rank': self.view_rank,
            'notes': self.notes,
            'floor_plan_type': self.floor_plan_type,
            'availability_date': self.availability_date,  # add availability date to the dictionary
            'is_sublease': self.is_sublease,  # add is_sublease to the dictionary
            'sublease_owner_name': self.sublease_owner_name,  # add sublease_owner_name to the dictionary
            'sublease_owner_phone': self.sublease_owner_phone  # add sublease_owner_phone to the dictionary
        }

    def __eq__(self, other):
        """Equality check based on unit_number and price."""
        if isinstance(other, Unit):
            return self.unit_number == other.unit_number
        return False

    def __hash__(self):
        """Hash based on unit_number and price."""
        return hash(self.unit_number)

    def __lt__(self, other):
        if isinstance(other, Unit):
            return int(self.unit_number) < int(other.unit_number)
        return False
