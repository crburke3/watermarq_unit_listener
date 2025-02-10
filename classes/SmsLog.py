from dataclasses import dataclass
from datetime import datetime

@dataclass
class SMSLog:
    """
    Represents an SMS log entry.
    """
    to_number: str
    from_number: str
    from_service: str
    message: str
    successful: bool
    timestamp: datetime = None

    def to_json(self):
        """
        Converts the SMSLog object to a JSON-compatible dictionary.
        """
        return {
            "to_number": self.to_number,
            "from_number": self.from_number,
            "from_service": self.from_service,
            "message": self.message,
            "successful": self.successful,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

    @classmethod
    def from_json(cls, json_data):
        """
        Creates an SMSLog object from a JSON dictionary.
        """
        timestamp = datetime.fromisoformat(json_data.get('timestamp')) if json_data.get('timestamp') else None
        return cls(
            to_number=json_data['to_number'],
            from_number=json_data['from_number'],
            from_service=json_data['from_service'],
            message=json_data['message'],
            successful=json_data['successful'],
            timestamp=timestamp
        )
