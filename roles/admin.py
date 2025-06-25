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
            # Get users and their profiles, excluding deleted users
            users = supabase.table("users").select("""
                userid, email, role, must_change_password, profile_completed, created_at, status,
                profile:profile(userid, bio, skills)
            """).neq("status", "Delete").execute().data
        except Exception as e:
            st.error(f"Failed to load users: {e}")
            users = []
    
        if users:
            # 🔍 Search & filter inputs
            email_search = st.text_input("Search by Email").lower()
            status_filter = st.selectbox("Filter by Status", options=["All", "Active", "Inactive"])
    
            # Build user table
            filtered_users = []
            for user in users:
                email = user.get("email", "").lower()
                status = user.get("status", "Active")
    
                if email_search and email_search not in email:
                    continue
                if status_filter != "All" and status != status_filter:
                    continue
    
                filtered_users.append({
                    "User ID": user.get("userid"),
                    "Email": user.get("email"),
                    "Role": user.get("role"),
                    "Status": status if user.get("role") != "Admin" else "N/A",
                    "Must Change Password": user.get("must_change_password"),
                    "Profile Completed": user.get("profile_completed"),
                    "Created At": user.get("created_at") or "-",
                    "Bio": user.get("profile", {}).get("bio", "-") if user.get("profile") else "-",
                    "Skills": user.get("profile", {}).get("skills", "-") if user.get("profile") else "-"
                })
    
            # Display static table for reference
            st.dataframe(pd.DataFrame(filtered_users), use_container_width=True)
    
            st.markdown("### 🛠 Manage User Status")
    
            for user in filtered_users:
                if user["Role"] == "Admin":
                    continue  # Skip Admins
    
                col1, col2, col3 = st.columns([4, 3, 2])
                with col1:
                    st.markdown(f"**{user['Email']}**")
                with col2:
                    current_status = user["Status"]
                    new_status = st.selectbox(
                        "Status",
                        ["Active", "Inactive", "Delete"],
                        index=["Active", "Inactive", "Delete"].index(current_status) if current_status in ["Active", "Inactive"] else 0,
                        key=f"status_select_{user['User ID']}"
                    )
                with col3:
                    if st.button("Update", key=f"update_btn_{user['User ID']}"):
                        if new_status == "Delete":
                            try:
                                supabase.table("users").delete().eq("userid", user["User ID"]).execute()
                                st.success(f"User {user['Email']} deleted permanently.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to delete user: {e}")
                        else:
                            try:
                                supabase.table("users").update({"status": new_status}).eq("userid", user["User ID"]).execute()
                                st.success(f"Status updated to {new_status} for {user['Email']}.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to update status: {e}")
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
