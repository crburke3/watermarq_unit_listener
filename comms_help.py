# from twilio.rest import Client
#
# # Twilio credentials (from your Twilio console)
#
# # Initialize Twilio client
# client = Client(account_sid, auth_token)
#
# # Send SMS
# message = client.messages.create(
#     body="Hello, this is a test message from Twilio!",  # Message content
#     from_='+17042705208',  # Your Twilio phone number
#     to='+17048062009'  # Recipient's phone number
# )
#
# print(f"Message sent with SID: {message.sid}")
#
import requests
from dotenv import load_dotenv
import os
load_dotenv()


def send_telegram_message(number: str, message:str):
    bot_token = os.getenv('telegram_bot_token')
    chat_id = '6175295125'
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    response = requests.post(url, data={'chat_id': chat_id, 'text': message})

    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message. Error: {response.status_code} | {response.text}")


def send_message(number: str, message: str):
    send_telegram_message(number, message)