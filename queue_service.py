from datetime import datetime, timedelta, timezone
from google.cloud import tasks_v2
import json
# Example usage:
import comms_help
import firebase_storing
from classes.FutureSMSRequest import FutureSMSRequest
from dotenv import load_dotenv
load_dotenv()


project = "random-447703"
location = "us-central1"


def queue_text_notification(phone_number: str, message: str, days_delay: int, seconds_delay: int = 0):
    """Creates a task for a given queue with an arbitrary payload."""
    queue = "watermarq-messenger-notifications"
    creds = firebase_storing.get_google_creds()
    client = tasks_v2.CloudTasksClient()

    parent = client.queue_path(project, location, queue)
    url = "https://us-central1-random-447703.cloudfunctions.net/watermarq_listener/process_sms"
    schedule_time = datetime.now(tz=timezone.utc) + timedelta(days=days_delay, seconds=seconds_delay)
    data = {
        "to_number": phone_number,
        "message": message
    }
    json_data = json.dumps(data).encode('utf-8')

    task = {
        "http_request": {
            "http_method": "POST",
            "url": url,
            "headers": {"Content-Type": "application/json"},
            "body": json_data,
        },
        "schedule_time": {
            "seconds": int(schedule_time.timestamp()),
        },
    }
    response = client.create_task(request={"parent": parent, "task": task})
    print(f"Created task {response.name}")


def process_sms(future_sms: FutureSMSRequest):
    comms_help.send_message(number=future_sms.to_number, message=future_sms.message)

