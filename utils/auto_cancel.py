from datetime import datetime, timezone, timedelta
from database import supabase
import streamlit as st  # Optional: only if you want to display errors in Streamlit

def cancel_expired_requests():
    try:
        # ✅ Get all pending requests
        response = supabase.table("mentorshiprequest") \
            .select("mentorshiprequestid, created_at, status") \
            .eq("status", "PENDING") \
            .execute()

        now = datetime.now(timezone.utc)

        for req in response.data:
            created_at = datetime.fromisoformat(req["created_at"])
            request_id = req["mentorshiprequestid"]

            # ✅ Cancel if older than 48 hours
            if now - created_at > timedelta(hours=48):
                supabase.table("mentorshiprequest") \
                    .update({"status": "CANCELLED_AUTO"}) \
                    .eq("mentorshiprequestid", request_id) \
                    .execute()

    except Exception as e:
        st.error(f"⚠️ Failed to auto-cancel expired requests: {e}")
