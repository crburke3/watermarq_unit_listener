import comms_help
import firebase_storing
from watching_service import run_watermarq_messaging


def check_units(args):
    latest_log = firebase_storing.get_most_recent_run_log()
    try:
        result = run_watermarq_messaging(args)
        if latest_log:
            if latest_log.error_message:
                comms_help.send_message("", "System functional again lfg")
        firebase_storing.save_run_log_to_firebase(successful=True)
        return result
    except Exception as e:
        err_message = f"Something failed: {e}"
        comms_help.send_telegram_message("", err_message)
        firebase_storing.save_run_log_to_firebase(successful=False, error=err_message)
        return {"error": err_message}, 400
