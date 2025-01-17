import comms_help
import firebase_storing
from watching_service import run_watermarq_messaging


def check_units(request):
    """
    Google Cloud Function to forward incoming SMS via Twilio.
    """
    # Log the request URL and method
    print(f"Request URL: {request.url}")
    print(f"Request method: {request.method}")
    print(f"Request headers: {dict(request.headers)}")

    # Log the request body (use request.get_data for raw payload)
    print(f"Request body: {request.get_data(as_text=True)}")
    latest_log = firebase_storing.get_most_recent_run_log()

    if "from_twillio" in request.url:
        print(f"recieved request from twilio: {request.form}")
        handle_message_reception(request)
    else:
        try:
            result = run_watermarq_messaging(request)
            if latest_log:
                if latest_log.error_message:
                    comms_help.send_telegram_message("", "System functional again lfg")
            firebase_storing.save_run_log_to_firebase(successful=True)
            return result
        except Exception as e:
            err_message = f"Something failed: {e}"
            comms_help.send_telegram_message("", err_message)
            firebase_storing.save_run_log_to_firebase(successful=False, error=err_message)
            return {"error": err_message}, 400


def handle_message_reception(args):
    return "", 200
