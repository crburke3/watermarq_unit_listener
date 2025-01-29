import comms_help
import firebase_storing
import helpers
import queue_service
import reception.primary_reception
import sublease_handling
from watching_service import run_watermarq_messaging
from flask import request, jsonify
from dotenv import load_dotenv
from classes.FutureSMSRequest import FutureSMSRequest  # Import your dataclass

load_dotenv()


def schedule_sms(request):
    """
    This Cloud Function receives a JSON request containing
    'to_number' and 'message' for a future SMS.
    """
    request_json = request.get_json(silent=True)

    if request_json and 'data' in request_json:
        try:
            # Parse the JSON data into a FutureSMSRequest object
            sms_request = FutureSMSRequest.from_json(request_json['data'])

            # Access and use the data
            to_number = sms_request.to_number
            message = sms_request.message

            return f"Scheduled SMS to {to_number} with message: {message}"

        except (KeyError, ValueError) as e:
            return f"Error parsing request: {e}", 400

    else:
        return "Invalid request format", 400


def check_units(request):
    """
    Google Cloud Function to forward incoming SMS via Twilio.
    """
    # Log the request URL and method
    try:
        print(f"Request URL: {request.url}")
        print(f"Request method: {request.method}")
        print(f"Request headers: {dict(request.headers)}")
        print(f"Request body: {request.get_data(as_text=True)}")
        request_json = request.get_json(silent=True)
        print(f"Request json: {request_json}")
    except Exception as e:
        print(f"Failed to parse body: {request}")



    if "from_twillio" in request.url:
        try:
            print(f"recieved request from twilio: {request.form}")
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
            return "handled reception", 200
        except Exception as e:
            print(f"Failed to handle from_twillio response: {e}")
            return jsonify({"error": str(e)}), 200


    elif "process_sms" in request.url:
        print(f"processing SMS")
        try:
            request_json = request.get_json(silent=True)
            print(f"Processing with json: {request_json}")
            if not request_json and 'to_number' in request_json and 'message' in request_json:
                raise Exception("invalid data format")
            sms_request = FutureSMSRequest.from_json(request_json)
            queue_service.process_sms(sms_request)
            return jsonify({"message": "success"}), 200
        except Exception as e:
            print(f"FAILED to process_sms: {e}")
            return jsonify({"error": str(e)}), 401


    elif "run_listener" in request.url:
        latest_log = firebase_storing.get_most_recent_run_log()
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

    else:
        return {"message", f"unknown route: {request.url}"}, 400
