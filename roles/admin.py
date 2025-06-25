import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import format_datetime
import streamlit as st
from database import supabase
from auth import register_user

def show():
    st.title("Admin Dashboard")
    st.info("Admin dashboard features: manage users, matches, and sessions.")

    tabs = st.tabs(["📝 Register", "👥 Users", "🔁 Requests", "📆 Sessions"])

    # 📝 Register Tab
    with tabs[0]:
        st.subheader("Register New User")
        with st.form("register_user"):
            email = st.text_input("User Email")
            role = st.selectbox("Assign Role", ["Mentor", "Mentee"])
            submitted = st.form_submit_button("Create")

            if submitted:
                message = register_user(email, role)
                st.success(message)
                st.rerun()

    # 👥 Users Tab
    with tabs[1]:
        st.subheader("All Users")
        try:
            users = supabase.table("users").select("*").execute().data
        except Exception as e:
            st.error(f"Failed to load users: {e}")
            users = []

        for user in users:
            with st.expander(f"📧 {user.get('email', 'No Email')}"):
                st.write(f"**ID:** {user.get('userid')}")
                st.write(f"**Role:** {user.get('role')}")
                st.write(f"**Must Change Password:** {user.get('must_change_password', '-')}")
                st.write(f"**Profile Completed:** {user.get('profile_completed', '-')}")
                st.write(f"**Created At:** {user.get('created_at', '-')}")

                confirm_key = f"confirm_delete_{user['userid']}"
                delete_key = f"delete_{user['userid']}"

                confirm = st.checkbox(f"✅ I understand that deleting {user['email']} is permanent", key=confirm_key)

                if confirm:
                    if st.button("❌ Confirm Delete User", key=delete_key):
                        try:
                            supabase.table("users").delete().eq("userid", user["userid"]).execute()
                            st.success(f"User {user['email']} deleted.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Deletion failed: {e}")
                else:
                    st.info("Check the box to confirm deletion.")

    # 🔁 Requests Tab
    with tabs[2]:
        st.subheader("Mentorship Requests")
        try:
            requests = supabase.table("mentorshiprequest") \
                .select("""
                    *,
                    mentee:users!mentorshiprequest_menteeid_fkey(email),
                    mentor:users!mentorshiprequest_mentorid_fkey(email)
                """).execute().data
        except Exception as e:
            st.error(f"Could not fetch mentorship requests: {e}")
            requests = []

        if requests:
            for req in requests:
                st.markdown(f"""
                - Mentee: **{req['mentee']['email']}**
                - Mentor: **{req['mentor']['email']}**
                - Status: **{req.get('status', 'Unknown')}**
                """)
        else:
            st.info("No mentorship requests found.")

    # 📆 Sessions Tab
    with tabs[3]:
        st.subheader("All Sessions")
        try:
            sessions = supabase.table("session") \
                .select("""
                    *,
                    mentee:users!session_menteeid_fkey(email),
                    mentor:users!session_mentorid_fkey(email)
                """).execute().data
        except Exception as e:
            st.error(f"Could not fetch sessions: {e}")
            sessions = []

        if sessions:
            for s in sessions:
                st.markdown(f"""
                - Mentor: **{s['mentor']['email']}**
                - Mentee: **{s['mentee']['email']}**
                - Date: {format_datetime(s['date'])}
                - Rating: {s.get('rating', '-') if s.get('rating') else '-'}
                """)
        else:
            st.info("No sessions found.")
