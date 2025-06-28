from datetime import datetime, timedelta, timezone
from dateutil import parser
from database import supabase
import streamlit as st

def cancel_expired_requests():
    try:
        response = supabase.table("mentorshiprequest") \
            .select("mentorshiprequestid, createdat, status") \
            .eq("status", "PENDING") \
            .execute()

        now = datetime.now(timezone.utc)

        for req in response.data:
            try:
                created_at = parser.isoparse(req["createdat"])
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)

                if now - created_at > timedelta(hours=48):
                    supabase.table("mentorshiprequest") \
                        .update({"status": "CANCELLED_AUTO"}) \
                        .eq("mentorshiprequestid", req["mentorshiprequestid"]) \
                        .execute()
            except Exception as inner_err:
                st.warning(f"Could not process request {req['mentorshiprequestid']}: {inner_err}")
    except Exception as e:
        st.error(f"⚠️ Failed to auto-cancel expired requests: {e}")
