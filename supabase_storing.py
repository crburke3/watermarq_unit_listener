import os
from classes.SmsLog import SMSLog
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

database_url = os.environ["SUPABASE_CONN_STRING"]
if not database_url:
    raise Exception("Failed to find SUPABASE_CONN_STRING in env")
supabase_key = os.environ["SUPABASE_KEY"]
if not supabase_key:
    raise Exception("Failed to find SUPABASE_KEY in env")
parsed_url = urlparse(database_url)
supabase_url = f"https://{parsed_url.hostname.replace('db.', '')}"
supa: Client = create_client(supabase_url, supabase_key)


def insert_sms_log(sms_log: SMSLog):
    """
    Inserts an SMSLog entry into the Supabase database.
    """
    try:
        data = sms_log.to_json()
        if not data["timestamp"]:
            data["timestamp"] = datetime.utcnow().isoformat()
        response = supa.table("sms_logs").insert(data).execute()
        return response
    except Exception as e:
        print(f"Failed to log sms_log: {e} | {sms_log}")
