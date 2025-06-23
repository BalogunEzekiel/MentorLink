# Mentor dashboard, availability management
import streamlit as st
from database import supabase
from utils.helpers import format_datetime

def show():
    st.title("Mentor Dashboard")
    st.info("View mentorship requests, manage availability, and see upcoming sessions.")

    user = st.session_state.user
    mentor_id = user["userid"]

    st.header("📥 Incoming Mentorship Requests")
    requests = supabase.table("mentorshiprequest") \
        .select("*, users!mentorshiprequest_menteeid_fkey(email)") \
        .eq("mentorid", mentor_id).eq("status", "PENDING").execute().data

    if requests:
        for req in requests:
            mentee_email = req["users"]["email"]
            st.markdown(f"**From:** {mentee_email}")
            col1, col2 = st.columns(2)
            if col1.button("Accept", key=f"accept_{req['mentorshiprequestid']}"):
                supabase.table("mentorshiprequest").update({"status": "ACCEPTED"}).eq("mentorshiprequestid", req["mentorshiprequestid"]).execute()
                st.success(f"Accepted request from {mentee_email}")
                st.experimental_rerun()
            if col2.button("Reject", key=f"reject_{req['mentorshiprequestid']}"):
                supabase.table("mentorshiprequest").update({"status": "REJECTED"}).eq("mentorshiprequestid", req["mentorshiprequestid"]).execute()
                st.warning(f"Rejected request from {mentee_email}")
                st.experimental_rerun()
    else:
        st.info("No pending requests.")

    st.header("📅 Scheduled Sessions")
    sessions = supabase.table("session") \
        .select("*, users!session_menteeid_fkey(email)") \
        .eq("mentorid", mentor_id).execute().data

    if sessions:
        for s in sessions:
            st.markdown(f"""
            #### Session with {s['users']['email']}
            - 🗓 **Date:** {format_datetime(s['date'])}
            - ⭐ **Rating:** {s.get('rating', 'Pending')}
            - 💬 **Feedback:** {s.get('feedback', 'Not submitted yet')}
            """)
    else:
        st.info("No upcoming or past sessions yet.")

from mentor_calendar import show_calendar
st.subheader("🗓 Visual Schedule")
show_calendar()
