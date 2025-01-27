import comms_help
import firebase_storing
import helpers
import reception.primary_reception
from watching_service import run_watermarq_messaging
from flask import request, jsonify
from dotenv import load_dotenv


load_dotenv()


def check_units(request):
    """
    Google Cloud Function to forward incoming SMS via Twilio.
    """
    # Log the request URL and method
    try:
        print(f"Request URL: {request.url}")
        print(f"Request method: {request.method}")
        print(f"Request headers: {dict(request.headers)}")

        # Log the request body (use request.get_data for raw payload)
        print(f"Request body: {request.get_data(as_text=True)}")
    except Exception as e:
        print(f"Failed to parse body: {request}")

    latest_log = firebase_storing.get_most_recent_run_log()
    if "from_twillio" in request.url:
        try:
            print(f"recieved request from twilio: {request.form}")
            handle_message_reception(request)
            return "handled reception", 200
        except Exception as e:
            print(f"Failed to handle from_twillio response: {e}")
            return "We had an error processing that :( Christian has been notified"
    else:
        proxy_url = helpers.get_random_proxy_url()
        print(f"using proxy url: {proxy_url}")
        try:
            result = run_watermarq_messaging(request, proxy_url=proxy_url)
            if latest_log:
                if latest_log.error_message:
                    comms_help.send_telegram_message("", "System functional again lfg")
            firebase_storing.save_run_log_to_firebase(successful=True)
            return result
        except Exception as e:
            err_message = f"Something failed: {e}"
            print(err_message)
            comms_help.send_telegram_message("", err_message)
            firebase_storing.save_run_log_to_firebase(successful=False, error=err_message, proxy=proxy_url)
            return {"error": err_message}, 400


def handle_message_reception(request):
    if request.method != "POST":
        return jsonify({"error": "Invalid request method. Use POST."}), 405

    # Parse incoming SMS data
    from_number = request.form.get("From")
    message_body = request.form.get("Body")

    if not from_number or not message_body:
        return jsonify({"error": "Missing required fields: 'From' or 'Body'"}), 400

    try:
        reception.primary_reception.handle_reception(from_number=from_number, raw_message=message_body)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
