from datetime import datetime
from typing import Optional, Union
import pytz

# Timezone definition for West Africa Time (WAT) - Lagos
WAT = pytz.timezone("Africa/Lagos")

def format_datetime_safe(dt: Optional[Union[str, datetime]], tz=WAT) -> str:
    """
    Safely formats a datetime or string date to a readable string in given timezone.
    Handles naive or aware datetime objects and common string formats gracefully.
    """
    if not dt:
        return "Unknown"
    
    try:
        # Parse if string
        if isinstance(dt, datetime):
            dt_obj = dt
        else:
            try:
                dt_obj = datetime.fromisoformat(dt.replace("Z", "+00:00"))
            except Exception:
                dt_obj = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S.%f")

        # ✅ Fix: Assume naive datetime is in WAT, not UTC
        if dt_obj.tzinfo is None:
            dt_obj = tz.localize(dt_obj)  # Assume it's in WAT, not UTC

        dt_local = dt_obj.astimezone(tz)
        return dt_local.strftime("%A, %d %B %Y at %I:%M %p")
    except Exception:
        return str(dt)

def format_datetime(dt_string: str) -> str:
    """
    Strict formatter for known UTC ISO datetime strings.
    
    Args:
        dt_string: datetime string in ISO format
    
    Returns:
        Formatted datetime string in WAT timezone like "01 Jan 2024 15:30"
        or "Invalid date" if parsing fails.
    """
    try:
        dt = datetime.strptime(dt_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        try:
            dt = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            return "Invalid date"
    
    dt_utc = pytz.utc.localize(dt)
    dt_local = dt_utc.astimezone(WAT)
    return dt_local.strftime("%d %b %Y %H:%M")

def get_session_status(start: Union[str, datetime], end: Union[str, datetime], tz=WAT) -> str:
    """
    Determine session status (Past, Current, Upcoming) based on current time and start/end times.
    
    Args:
        start: start datetime string or object
        end: end datetime string or object
        tz: timezone to compare against (default: WAT)
    
    Returns:
        Status string: '🟥 Past', '🟨 Ongoing', or '🟩 Upcoming'
    """
    def to_datetime(dt):
        if isinstance(dt, datetime):
            return dt
        try:
            return datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except Exception:
            return datetime.strptime(dt, "%Y-%m-%d %H:%M:%S.%f")

    try:
        start_dt = to_datetime(start)
        end_dt = to_datetime(end)

        if start_dt.tzinfo is None:
            start_dt = pytz.utc.localize(start_dt)
        if end_dt.tzinfo is None:
            end_dt = pytz.utc.localize(end_dt)

        now = datetime.now(pytz.utc).astimezone(tz)
        start_local = start_dt.astimezone(tz)
        end_local = end_dt.astimezone(tz)

        if now < start_local:
            return "🟩 Upcoming"
        elif start_local <= now <= end_local:
            return "🟨 Ongoing"
        else:
            return "🟥 Past"
    except Exception:
        return "Unknown"
