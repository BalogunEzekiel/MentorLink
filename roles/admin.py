# Admin dashboard view logic
import streamlit as st
from database import supabase
from utils.helpers import format_datetime
from auth import register_user

def show():
    st.title("Admin Dashboard")
    st.info("Admin dashboard features will go here: manage users, matches, and sessions.")

    st.subheader("📝 Register New User")
    with st.form("register_user"):
        email = st.text_input("User Email")
        role = st.selectbox("Assign Role", ["Mentor", "Mentee"])
        submitted = st.form_submit_button("Create")

        if submitted:
            message = register_user(email, role)
            st.success(message)

    st.header("👥 All Users")
    users = supabase.table("users").select("*").execute().data
    for user in users:
        st.markdown(f"""
        - **Email:** {user['email']}
        - **Role:** {user['role']}
        """)

    st.header("🔁 Mentorship Requests")
    requests = supabase.table("mentorshiprequest") \
        .select("*, users!mentorshiprequest_menteeid_fkey(email), users!mentorshiprequest_mentorid_fkey(email)") \
        .execute().data

    for req in requests:
        st.markdown(f"""
        - Mentee ID: **{req['menteeid']}**
        - Mentor ID: **{req['mentorid']}**
        - Status: **{req['status']}**
        """)

    st.header("📆 All Sessions")
    sessions = supabase.table("session") \
        .select("*, users!session_menteeid_fkey(email), users!session_mentorid_fkey(email)") \
        .execute().data

    for s in sessions:
        st.markdown(f"""
        - Mentor ID: {s['mentorid']}
        - Mentee ID: {s['menteeid']}
        - Date: {format_datetime(s['date'])}
        - Rating: {s.get('rating', '-')}
        """)
