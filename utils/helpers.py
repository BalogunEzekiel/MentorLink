# utils/helpers.py

from datetime import datetime
from typing import Optional
import pytz

# --- Safe formatter that handles multiple input types
def format_datetime_safe(dt: Optional[str or datetime]) -> str:
    if not dt:
        return "Unknown"
    if isinstance(dt, datetime):
        return dt.strftime("%A, %d %B %Y at %I:%M %p")
    try:
        parsed = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        return parsed.strftime("%A, %d %B %Y at %I:%M %p")
    except Exception:
        return str(dt)

# --- Formatter that converts UTC string to localized Lagos time
def format_datetime(dt_string: str) -> str:
    try:
        # Try ISO UTC with milliseconds
        dt = datetime.strptime(dt_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        try:
            # Try standard SQL format
            dt = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            return "Invalid date"

    # Convert UTC to Africa/Lagos timezone
    utc = pytz.utc
    local_tz = pytz.timezone("Africa/Lagos")
    dt_utc = utc.localize(dt)
    dt_local = dt_utc.astimezone(local_tz)

    return dt_local.strftime("%d %b %Y %H:%M")
