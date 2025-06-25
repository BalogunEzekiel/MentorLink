import streamlit as st
from database import supabase
from utils.helpers import format_datetime
from emailer import send_email

def show():
    st.title("Mentee Dashboard")
    st.info("Browse mentors, request sessions, and track bookings.")
    user_id = st.session_state.user["userid"]

    # Create tabs
    tabs = st.tabs(["🧑‍🏫 Browse Mentors", "📄 My Requests", "📆 My Sessions"])

    # 🧑‍🏫 Browse Mentors Tab
    with tabs[0]:
        st.subheader("Browse Available Mentors")
        mentors = supabase.table("users").select("*").eq("role", "Mentor").execute().data

        for mentor in mentors:
            st.markdown(f"**{mentor['email']}**")
            if st.button("Request Mentorship", key=mentor["userid"]):
                supabase.table("mentorshiprequest").insert({
                    "mentorid": mentor["userid"],
                    "menteeid": user_id,
                    "status": "PENDING"
                }).execute()
                st.success("Mentorship request sent!")

    # 📄 My Requests Tab
    with tabs[1]:
        st.subheader("Your Mentorship Requests")
        requests = supabase.table("mentorshiprequest") \
            .select("*, users!mentorshiprequest_mentorid_fkey(email)") \
            .eq("menteeid", user_id).execute().data

        if requests:
            for req in requests:
                st.markdown(f"""
                - 🧑 Mentor: **{req['users']['email']}**
                - Status: **{req['status']}**
                """)
        else:
            st.info("You have not made any mentorship requests yet.")

    # 📆 My Sessions Tab
    with tabs[2]:
        st.subheader("Your Mentorship Sessions")
        sessions = supabase.table("session") \
            .select("*, users!session_mentorid_fkey(email)") \
            .eq("menteeid", user_id).execute().data

        if sessions:
            for s in sessions:
                st.markdown(f"""
                #### With: {s['users']['email']}
                - Date: {format_datetime(s['date'])}
                - Rating: {
