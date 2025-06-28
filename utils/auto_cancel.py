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

        now = datetime.now(timezone.utc)  # Timezone-aware

        for req in response.data:
            created_raw = req["createdat"]

            try:
                # Robustly parse any datetime string and force to UTC
                created_at = parser.isoparse(created_raw)

                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                else:
                    created_at = created_at.astimezone(timezone.utc)

                if now - created_at > timedelta(hours=48):
                    supabase.table("mentorshiprequest") \
                        .update({"status": "CANCELLED_AUTO"}) \
                        .eq("mentorshiprequestid", req["mentorshiprequestid"]) \
                        .execute()

            except Exception as inner_err:
                st.warning(f"⚠️ Error processing request ID {req['mentorshiprequestid']}: {inner_err}")

    except Exception as e:
        st.warning(f"⚠️ Failed to auto-cancel expired requests: {e}")
