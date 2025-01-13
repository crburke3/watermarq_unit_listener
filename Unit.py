
class Unit:
    def __init__(self, unit_number, price=None, is_exterior_facing=None, primary_exterior_face=None,
                 is_corner_unit=None, corner_type=None, size_rank=None, view_rank=None, notes=None,
                 floor_plan_type=None):
        self.unit_number = unit_number
        self.price = price
        self.is_exterior_facing = is_exterior_facing
        self.primary_exterior_face = primary_exterior_face
        self.is_corner_unit = is_corner_unit
        self.corner_type = corner_type
        self.size_rank = size_rank
        self.view_rank = view_rank
        self.notes = notes
        self.floor_plan_type=floor_plan_type

    def num_rooms(self):
        if not self.floor_plan_type: return None
        plan_type = self.floor_plan_type.lower()
        if "studio" in plan_type: return 1
        if "one bedroom" in plan_type: return 1
        if "two bedroom" in plan_type: return 2
        if "three bedroom" in plan_type: return 3
        return None

    def __repr__(self):
        emojis = ""
        emojis += "🪟" if self.is_exterior_facing else ""
        emojis += "🥇" if self.is_corner_unit else ""
        val = f"{self.unit_number}{emojis} {self.price}"
        val += f" {self.num_rooms()} rooms" if self.floor_plan_type else ""
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
            floor_plan_type=json_data.get('floor_plan_type', None)
        )

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
            'floor_plan_type': self.floor_plan_type
        }

    def __eq__(self, other):
        """Equality check based on unit_number and price."""
        if isinstance(other, Unit):
            return self.unit_number == other.unit_number
        return False

    def __hash__(self):
        """Hash based on unit_number and price."""
        return hash((self.unit_number, self.price))

    def __lt__(self, other):
        if isinstance(other, Unit):
            return int(self.unit_number) < int(other.unit_number)
        return False
