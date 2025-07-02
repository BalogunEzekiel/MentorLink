from datetime import datetime, timedelta, timezone
from dateutil import parser
from database import supabase
import streamlit as st

def cancel_expired_requests():
    try:
        pending_requests = supabase.table("mentorshiprequest") \
            .select("mentorshiprequestid, createdat, status") \
            .eq("status", "PENDING") \
            .execute()

        now_utc = datetime.now(timezone.utc)

        for req in pending_requests.data:
            try:
                created_at = parser.isoparse(req["createdat"])
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)

                # Cancel if older than 48 hours
                if now_utc - created_at > timedelta(hours=48):
                    supabase.table("mentorshiprequest") \
                        .update({"status": "CANCELLED_AUTO"}) \
                        .eq("mentorshiprequestid", req["mentorshiprequestid"]) \
                        .execute()

            except Exception as inner_err:
                st.warning(f"⚠️ Skipped request {req.get('mentorshiprequestid')} due to: {inner_err}")

    except Exception as outer_err:
        st.error(f"❌ Failed to process expired mentorship requests: {outer_err}")
