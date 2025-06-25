import streamlit as st
from database import supabase
from utils.helpers import format_datetime
from mentor_calendar import show_calendar

def show():
    st.title("Mentor Dashboard")
    st.info("View mentorship requests, manage availability, and see upcoming sessions.")

    user = st.session_state.user
    mentor_id = user["userid"]

    # Create tabs for navigation
    tabs = st.tabs(["📥 Requests", "📅 Sessions", "🗓 Calendar"])

    # 📥 Incoming Mentorship Requests Tab
    with tabs[0]:
        st.subheader("Incoming Mentorship Requests")
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
                    st.rerun()
                if col2.button("Reject", key=f"reject_{req['mentorshiprequestid']}"):
                    supabase.table("mentorshiprequest").update({"status": "REJECTED"}).eq("mento
