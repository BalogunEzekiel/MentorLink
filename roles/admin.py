import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import format_datetime
import streamlit as st
from database import supabase
from auth import register_user
import pandas as pd

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
            # Get users and their profiles, including status
            users = supabase.table("users").select("""
                userid, email, role, must_change_password, profile_completed, created_at, status,
                profile:profile(userid, bio, skills)
            """).neq("status", "Delete").execute().data  # Exclude deleted users
        except Exception as e:
            st.error(f"Failed to load users: {e}")
            users = []
    
        if users:
            # Flatten user records
            flat_users = []
            for user in users:
                flat_users.append({
                    "User ID": user.get("userid"),
                    "Email": user.get("email"),
                    "Role": user.get("role"),
                    "Status": user.get("status") if user.get("role") != "Admin" else "N/A",  # No status for Admins
                    "Must Change Password": user.get("must_change_password"),
                    "Profile Completed": user.get("profile_completed"),
                    "Created At": user.get("created_at"),
                    "Bio": user.get("profile", {}).get("bio", "-") if user.get("profile") else "-",
                    "Skills": user.get("profile", {}).get("skills", "-") if user.get("profile") else "-"
                })
    
            df = pd.DataFrame(flat_users)
    
            # Email search box
            email_search = st.text_input("Search by Email").lower()
            if email_search:
                df = df[df["Email"].str.lower().str.contains(email_search)]
    
            # Status filter dropdown
            status_filter = st.selectbox("Filter by Status", options=["All", "Active", "Inactive"])
            if status_filter != "All":
                df = df[df["Status"] == status_filter]
    
            st.dataframe(df, use_container_width=True)
    
        else:
            st.info("No users found.")
        
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
