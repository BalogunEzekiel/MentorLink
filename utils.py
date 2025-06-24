# utils.py
from datetime import datetime

def format_datetime(dt_string):
    try:
        return datetime.fromisoformat(dt_string).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return dt_string  # return raw string if formatting fails
