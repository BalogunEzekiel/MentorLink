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
                userid, email, role, must_change_password, profile_completed, created_at, status
            """).neq("status", "Delete").execute().data
        except Exception as e:
            st.error(f"Failed to load users: {e}")
            users = []
    
        if users:
            email_search = st.text_input("Search by Email").lower()
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive"])
    
            display_users = []
            for i, user in enumerate(users, 1):
                email = user.get("email", "").lower()
                status = user.get("status", "Active")
                if email_search and email_search not in email:
                    continue
                if status_filter != "All" and status != status_filter:
                    continue
    
                display_users.append({
                    "index": i,
                    "userid": user.get("userid"),
                    "email": user.get("email"),
                    "role": user.get("role"),
                    "status": status,
                    "must_change_password": user.get("must_change_password"),
                    "profile_completed": user.get("profile_completed"),
                    "created_at": user.get("created_at") or "-"
                })
    
            st.markdown("#### User Table")
    
            # Custom CSS to style the table
            st.markdown("""
            <style>
            .user-table {
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed;
            }
            .user-table th, .user-table td {
                border: 1px solid #ccc;
                padding: 6px;
                text-align: left;
                word-wrap: break-word;
                font-size: 0.9rem;
            }
            .user-table th {
                background-color: #f5f5f5;
            }
            </style>
            """, unsafe_allow_html=True)
    
            # HTML header row
            st.markdown("""
            <table class="user-table">
                <tr>
                    <th>#</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Must Change</th>
                    <th>Profile Done</th>
                    <th>Created At</th>
                    <th>Status</th>
                    <th>Action</th>
                </tr>
            """, unsafe_allow_html=True)
    
            # Streamlit elements (status select + button) row-by-row
            for user in display_users:
                cols = st.columns([0.3, 2, 1, 1.2, 1.2, 1.5, 1.5, 1])
                cols[0].markdown(f"{user['index']}")
                cols[1].markdown(user["email"])
                cols[2].markdown(user["role"])
                cols[3].markdown(str(user["must_change_password"]))
                cols[4].markdown(str(user["profile_completed"]))
                cols[5].markdown(str(user["created_at"]))
    
                if user["role"] == "Admin":
                    cols[6].markdown("N/A")
                    cols[7].markdown("🚫")
                else:
                    new_status = cols[6].selectbox(
                        "",
                        ["Active", "Inactive", "Delete"],
                        index=["Active", "Inactive", "Delete"].index(user["status"]),
                        key=f"status_{user['userid']}"
                    )
                    if cols[7].button("Update", key=f"update_{user['userid']}"):
                        try:
                            if new_status == "Delete":
                                supabase.table("users").delete().eq("userid", user["userid"]).execute()
                                st.success(f"Deleted user: {user['email']}")
                            else:
                                supabase.table("users").update({"status": new_status}).eq("userid", user["userid"]).execute()
                                st.success(f"Updated {user['email']} to {new_status}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to update user: {e}")
    
            # Close table
            st.markdown("</table>", unsafe_allow_html=True)
    
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
