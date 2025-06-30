# utils/session_creator.py

from datetime import timedelta
from typing import List, Optional

def is_time_slot_conflicting(new_start, new_end, existing_sessions):
    for s in existing_sessions:
        existing_start = s.get("date")
        if not existing_start:
            continue
        existing_end = existing_start + timedelta(hours=1)  # assuming 1 hour sessions
        if (new_start < existing_end and new_end > existing_start):
            return True
    return False

def create_session_if_available(supabase, mentorid, menteeid, new_start, new_end):
    try:
        # 🟢 Fetch existing sessions using 'date' column
        existing_sessions = supabase.table("session") \
            .select("date") \
            .eq("mentorid", mentorid) \
            .execute() \
            .data

        # 🟢 Convert timestamps to datetime objects
        for session in existing_sessions:
            if session.get("date"):
                session["date"] = datetime.fromisoformat(session["date"].replace("Z", "+00:00"))

        if is_time_slot_conflicting(new_start, new_end, existing_sessions):
            return False, "❌ Time slot conflicts with an existing session."

        supabase.table("session").insert({
            "mentorid": mentorid,
            "menteeid": menteeid,
            "date": new_start.isoformat(),
        }).execute()

        return True, "✅ Session created successfully."
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False, f"❌ Error: {str(e)}"
