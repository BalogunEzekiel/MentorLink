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
            users = supabase.table("users").select("""
                userid,
                email,
                role,
                must_change_password,
                profile_completed,
                created_at,
                status,
                profile:profile(userid, bio, skills)
            """).execute().data
        except Exception as e:
            st.error(f"Failed to load users: {e}")
            users = []
    
        if users:
            # 🔍 Search & Filter UI
            search_email = st.text_input("Search by Email").lower()
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive"])
    
            # Flatten user data
            display_users = []
            for user in users:
                email = user.get("email", "").lower()
                status = user.get("status", "Active")
    
                if search_email and search_email not in email:
                    continue
                if status_filter != "All" and status != status_filter:
                    continue
    
                display_users.append({
                    "User ID": user.get("userid"),
                    "Email": user.get("email"),
                    "Role": user.get("role"),
                    "Status": status,
                    "Must Change Password": user.get("must_change_password"),
                    "Profile Completed": user.get("profile_completed"),
                    "Created At": pd.to_datetime(user.get("created_at")).strftime("%Y-%m-%d %H:%M:%S"),
                    "Bio": user.get("profile", {}).get("bio", "-") if user.get("profile") else "-",
                    "Skills": user.get("profile", {}).get("skills", "-") if user.get("profile") else "-"
                })
    
            # 📊 Display table
            df = pd.DataFrame(display_users)
            st.dataframe(df, use_container_width=True)
    
            st.markdown("---")
            st.markdown("### 🔄 Update User Status")
    
            # 🔧 Allow status change (excluding Admins)
            for user in display_users:
                if user["Role"] == "Admin":
                    continue  # Skip Admins
    
                col1, col2, col3 = st.columns([4, 3, 2])
                with col1:
                    st.markdown(f"**{user['Email']}**")
                with col2:
                    status = st.selectbox(
                        "Change Status",
                        ["Active", "Inactive", "Delete"],
                        index=["Active", "Inactive", "Delete"].index(user["Status"]) if user["Status"] in ["Active", "Inactive"] else 0,
                        key=f"status_{user['User ID']}"
                    )
                with col3:
                    if st.button("Apply", key=f"apply_{user['User ID']}"):
                        if status == "Delete":
                            try:
                                supabase.table("users").delete().eq("userid", user["User ID"]).execute()
                                st.success(f"Deleted user: {user['Email']}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting user: {e}")
                        else:
                            try:
                                supabase.table("users").update({"status": status}).eq("userid", user["User ID"]).execute()
                                st.success(f"Updated {user['Email']} to {status}")
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
