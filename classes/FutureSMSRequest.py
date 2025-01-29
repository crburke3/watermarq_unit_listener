from dataclasses import dataclass
from datetime import datetime

@dataclass
class FutureSMSRequest:
  """
  Represents an SMS message request scheduled for future delivery.
  """
  to_number: str
  message: str
  original_time: datetime
  actual_time: datetime = None

  def to_json(self):
    """
    Converts the FutureSMSRequest object to a JSON string.
    """
    json_data = {
        "to_number": self.to_number,
        "message": self.message,
        "original_time": self.original_time.isoformat() if self.original_time else None,
        "actual_time": self.actual_time.isoformat() if self.actual_time else None
    }
    return json_data

  @classmethod
  def from_json(cls, json_data):
    """
    Creates a FutureSMSRequest object from a JSON string or dictionary.
    """
    original_time = datetime.fromisoformat(json_data.get('original_time')) if json_data.get('original_time') else None
    actual_time = datetime.fromisoformat(json_data.get('actual_time')) if json_data.get('actual_time') else None
    return cls(
        to_number=json_data['to_number'],
        message=json_data['message'],
        original_time=original_time,
        actual_time=actual_time
    )