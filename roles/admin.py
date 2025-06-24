# Admin dashboard view logic
import streamlit as st
from database import supabase
from utils.helpers import format_datetime
from auth import register_user

def show():
    st.title("Admin Dashboard")
    st.info("Admin dashboard features will go here: manage users, matches, and sessions.")

    # Register new user
    st.subheader("📝 Register New User")
    with st.form("register_user"):
        email = st.text_input("User Email")
        role = st.selectbox("Assign Role", ["Mentor", "Mentee"])
        submitted = st.form_submit_button("Create")

        if submitted:
            message = register_user(email, role)
            st.success(message)
            st.rerun()

    # All users
    st.header("👥 All Users")
    users = supabase.table("users").select("*").execute().data

    if users:
        for user in users:
            with st.expander(f"📧 {user['email']}"):
                st.write(f"**ID:** {user['id']}")
                st.write(f"**Role:** {user['role']}")
                st.write(f"**Must Change Password:** {user.get('must_change_password')}")
                st.write(f"**Profile Completed:** {user.get('profile_completed')}")
                st.write(f"**Created At:** {user.get('created_at')}")

                delete_key = f"delete_{user['id']}"
                if st.button("❌ Delete User", key=delete_key):
                    supabase.table("users").delete().eq("id", user["id"]).execute()
                    st.success(f"User {user['email']} deleted.")
                    st.rerun()
    else:
        st.info("No users found.")

    # Mentorship requests
    st.header("🔁 Mentorship Requests")
    requests = supabase.table("mentorshiprequest") \
        .select("*, users!mentorshiprequest_menteeid_fkey(email), users!mentorshiprequest_mentorid_fkey(email)") \
        .execute().data

    if requests:
        for req in requests:
            st.markdown(f"""
            - Mentee: **{req['users']['email']}**
            - Mentor ID: **{req['mentorid']}**
            - Status: **{req['status']}**
            """)
    else:
        st.info("No mentorship requests found.")

    # All sessions
    st.header("📆 All Sessions")
    sessions = supabase.table("session") \
        .select("*, users!session_menteeid_fkey(email), users!session_mentorid_fkey(email)") \
        .execute().data

    if sessions:
        for s in sessions:
            st.markdown(f"""
            - Mentor: **{s['users']['email']}**
            - Mentee ID: **{s['menteeid']}**
            - Date: {format_datetime(s['date'])}
            - Rating: {s.get('rating', '-')}
            """)
    else:
        st.info("No sessions found.")
