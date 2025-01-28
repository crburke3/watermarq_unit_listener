import comms_help
import firebase_storing
import helpers
import reception.primary_reception
import sublease_handling
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
        print(f"Request body: {request.get_data(as_text=True)}")
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



    elif "add_sublease" in request.url:
        if request.method != "POST":
            return jsonify({"error": "Invalid request method. Use POST."}), 405
        try:
            apt_number = request.form.get("unit_number")
            subleaser_name = request.form.get("subleaser_name")
            subleaser_phone = request.form.get("subleaser_phone_number")
            floor_plan_type = request.form.get("floor_plan_type")
            price = request.form.get("price")
            availability_date = request.form.get("availability_date")
            notes = request.form.get("notes", None)
            if not apt_number or not subleaser_name or not subleaser_phone or not price:
                return jsonify({"error": "Missing required fields: 'unit_number' or 'subleaser_name' or 'subleaser_phone_number' or 'price'"}), 400
            new_unit = sublease_handling.add_sublease_unit(
                unit_number=apt_number,
                price=price,
                subleaser_name=subleaser_name,
                subleaser_phone_number=subleaser_phone,
                availability_date=availability_date,
                floor_plan_type=floor_plan_type,
                notes=notes)
            return jsonify({"unit": new_unit.to_dict()}), 401
        except Exception as e:
            return jsonify({"error": str(e)}), 401



    elif "remove_sublease" in request.url:
        try:
            unit_number = request.form.get("unit_number")
            sublease_handling.remove_sublease_unit(unit_number=unit_number)
        except Exception as e:
            return jsonify({"error": str(e)}), 401



    else:
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


