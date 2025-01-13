from typing import Dict
from datetime import datetime

class RunLog:
    def __init__(self, timestamp: datetime, success: bool, error_message: str = None):
        self.timestamp = timestamp
        self.success = success
        self.error_message = error_message

    def __repr__(self):
        return (f"RunLog(timestamp={self.timestamp.isoformat()}, success={self.success}, "
                f"error_message={self.error_message})")

    @classmethod
    def from_dict(cls, data: Dict) -> 'RunLog':
        """
        Create a RunLog instance from a dictionary.
        Converts timestamp string to datetime.
        """
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            success=data['success'],
            error_message=data.get('error_message')  # Use .get to handle optional field
        )

    def to_dict(self) -> Dict:
        """
        Convert the RunLog instance to a dictionary.
        Converts datetime to ISO 8601 string.
        """
        return {
            'timestamp': self.timestamp.isoformat(),
            'success': self.success,
            'error_message': self.error_message
        }
