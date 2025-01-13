import comms_help
from watching_service import run_watermarq_messaging


def check_units(args):
    try:
        return run_watermarq_messaging(args)
    except Exception as e:
        err_message = f"Something failed: {e}"
        comms_help.send_telegram_message("", err_message)
        raise E
