from datetime import datetime, timedelta, timezone
from database import supabase
import streamlit as st

def cancel_expired_requests():
    try:
        response = supabase.table("mentorshiprequest") \
            .select("mentorshiprequestid, createdat, status") \
            .eq("status", "PENDING") \
            .execute()

        now = datetime.now(timezone.utc)  # ✅ Aware datetime

        for req in response.data:
            created_str = req["createdat"]

            # ✅ Make sure this is also timezone-aware
            created_at = datetime.fromisoformat(created_str)
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)

            if now - created_at > timedelta(hours=48):
                supabase.table("mentorshiprequest") \
                    .update({"status": "CANCELLED_AUTO"}) \
                    .eq("mentorshiprequestid", req["mentorshiprequestid"]) \
                    .execute()

    except Exception as e:
        st.warning(f"⚠️ Failed to auto-cancel expired requests: {e}")
