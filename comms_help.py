import requests
from dotenv import load_dotenv
import os
from twilio.rest import Client
import json
from pprint import pprint


load_dotenv()


def send_telegram_message(number: str, message: str):
    bot_token = os.getenv('telegram_bot_token')
    chat_id = '6175295125'
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    response = requests.post(url, data={'chat_id': chat_id, 'text': message})
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message. Error: {response.status_code} | {response.text}")


def send_text(number: str, message: str):
    try:
        account_sid = os.getenv('twilio_sid')
        auth_token = os.getenv('twilio_auth_token')
        client = Client(account_sid, auth_token)
        resp = client.messages.create(to=number, from_="+17042705208", body=message)
        print(f"successfully sent text: {resp.sid} | {resp.status}")
        pprint(vars(resp))
    except Exception as e:
        print(f"Failed to send text: {e}")


def send_message(number: str, message: str):
    send_text(number, message)
    send_telegram_message(number, message)

