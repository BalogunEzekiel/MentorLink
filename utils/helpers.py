from datetime import datetime
from typing import Optional
import pytz

# Timezone definition
WAT = pytz.timezone("Africa/Lagos")

# --- Safe formatter that handles both datetime objects and strings
def format_datetime_safe(dt: Optional[str or datetime], tz=WAT) -> str:
    if not dt:
        return "Unknown"
    try:
        # If it's already a datetime object
        if isinstance(dt, datetime):
            dt_obj = dt
        else:
            # Parse ISO or SQL format with fallback
            try:
                dt_obj = datetime.fromisoformat(dt.replace("Z", "+00:00"))
            except:
                dt_obj = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S.%f")
        
        # Ensure timezone awareness
        if dt_obj.tzinfo is None:
            dt_obj = pytz.utc.localize(dt_obj)
        dt_local = dt_obj.astimezone(tz)

        return dt_local.strftime("%A, %d %B %Y at %I:%M %p")
    except Exception:
        return str(dt)

# --- Strict formatter for known UTC ISO string input (fallback format)
def format_datetime(dt_string: str) -> str:
    try:
        dt = datetime.strptime(dt_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        try:
            dt = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            return "Invalid date"

    # Convert to WAT
    dt_utc = pytz.utc.localize(dt)
    dt_local = dt_utc.astimezone(WAT)
    return dt_local.strftime("%d %b %Y %H:%M")
