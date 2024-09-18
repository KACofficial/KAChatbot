from datetime import datetime


def get_current_time(format: str) -> str:
    current_date = datetime.now()
    return current_date.strftime(format)
