# utils/session_creator.py

from datetime import datetime
from typing import List, Optional

# --- Format datetime safely for display
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

# --- Check for time slot conflict with existing sessions
def is_time_slot_conflicting(new_start: datetime, new_end: datetime, existing_sessions: List[dict]) -> bool:
    for session in existing_sessions:
        start = datetime.fromisoformat(session['start'])
        end = datetime.fromisoformat(session['end'])
        if start < new_end and new_start < end:
            return True
    return False

# --- Create session if slot is available
def create_session_if_available(supabase, mentorid: str, menteeid: str, new_start: datetime, new_end: datetime):
    existing_sessions = supabase.table("session") \
        .select("start, end") \
        .eq("mentorid", mentorid) \
        .execute() \
        .data

    if is_time_slot_conflicting(new_start, new_end, existing_sessions):
        return False, "⚠️ Selected time overlaps with another session."

    try:
        supabase.table("session").insert({
            "mentorid": mentorid,
            "menteeid": menteeid,
            "date": new_start.isoformat(),  # single timestamp field
            "start": new_start.isoformat(),
            "end": new_end.isoformat()
        }).execute()
        return True, "✅ Session successfully created."
    except Exception as e:
        return False, f"❌ Failed to create session: {e}"
