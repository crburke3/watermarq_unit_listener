import datetime

import requests
from dotenv import load_dotenv
import os
from twilio.rest import Client
import time
import supabase_storing
from classes.SmsLog import SMSLog

TWILIO_NUMBER = "+17042705208"
CHRISTIANS_NUMBER = "+17048062009"

load_dotenv()

account_sid = os.getenv('twilio_sid')
auth_token = os.getenv('twilio_auth_token')
twilio_client = Client(account_sid, auth_token)
is_dev = os.getenv('is_dev')
print(f"in dev: {is_dev}")


def send_telegram_message(number: str, message: str):
    bot_token = os.getenv('telegram_bot_token')
    chat_id = '6175295125'
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    response = requests.post(url, data={'chat_id': chat_id, 'text': message})
    if response.status_code == 200:
        print("Telegram Message sent successfully!")
    else:
        print(f"Failed to send message. Error: {response.status_code} | {response.text}")


def send_text(number: str, message: str, chunk_size: int = 800):
    print(f"sending text to {number}")

    try:
        # Split message into chunks respecting newlines
        message_chunks = []
        start = 0
        while start < len(message):
            end = min(start + chunk_size, len(message))
            chunk = message[start:end]

            # Find the last newline within the chunk
            last_newline = chunk.rfind('\n')
            if last_newline != -1 and end < len(message):  # Split at newline
                split_point = start + last_newline + 1
            else:  # No newline or last chunk
                split_point = end

            message_chunks.append(message[start:split_point].rstrip())
            start = split_point

        # Send each chunk using Twilio
        should_sleep = len(message_chunks) > 1
        for chunk in message_chunks:
            if is_dev:
                print(f"DEV SKIPPING OUTBOUND SMS: {number} | {message}")
                return
            else:
                send_twillio_text(number, chunk)
                if should_sleep:
                    time.sleep(1)
    except Exception as e:
        print(f"Failed to send text: {e}")


def send_twillio_text(number: str, message: str):
    resp = twilio_client.messages.create(to=number, from_=TWILIO_NUMBER, body=message)
    print(f"[TEXT:Sent] {number} | {message} | {resp.sid} | {resp.status}")
    successful = resp.error_message is None
    sms_log = SMSLog(to_number=number,
                     from_number=TWILIO_NUMBER,
                     from_service="TWILLIO",
                     message=message,
                     successful=successful,
                     timestamp=datetime.datetime.now()
                     )
    supabase_storing.insert_sms_log(sms_log)


def send_message(number: str, message: str):
    send_telegram_message(number, f"TO: {number}: "+ message)
    send_text(number, message)


def send_image(number: str, message: str, image_url: str):
    send_telegram_message(number, message + f"\n\n\n{image_url}")
    resp = twilio_client.messages.create(
        body=message,  # Message content
        from_=TWILIO_NUMBER,  # Your Twilio number
        to=number,  # Recipient's phone number
        media_url=[image_url]  # URL of the media file
    )
    print(f"[TEXT:sent] sent image: {resp.sid} | {resp.status} | {image_url}")
