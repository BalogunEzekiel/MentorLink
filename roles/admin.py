import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
import streamlit as st
from database import supabase
from auth import register_user
import pandas as pd

# ✅ Safe datetime formatter
def format_datetime(dt):
    if not dt:
        return "Unknown"

    if isinstance(dt, datetime):
        return dt.strftime("%A, %d %B %Y at %I:%M %p")

    try:
        parsed = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        return parsed.strftime("%A, %d %B %Y at %I:%M %p")
    except Exception:
        return str(dt)

def show():
    st.title("Admin Dashboard")
    st.info("Admin dashboard features: manage users, matches, and sessions.")

    tabs = st.tabs(["📝 Register", "👥 Users", "🔁 Requests", "📆 Sessions"])

    # 📝 Register Tab
    with tabs[0]:
        st.subheader("Register New User")
    
        # Initialize session state
        if "new_user_email" not in st.session_state:
            st.session_state.new_user_email = ""
        if "new_user_role" not in st.session_state:
            st.session_state.new_user_role = ""
    
        with st.form("register_user"):
            st.session_state.new_user_email = st.text_input("User Email", value=st.session_state.new_user_email)
    
            roles = ["", "Mentor", "Mentee"]
            role_index = roles.index(st.session_state.new_user_role) if st.session_state.new_user_role in roles else 0
            st.session_state.new_user_role = st.selectbox("Assign Role", roles, index=role_index)
    
            submitted = st.form_submit_button("Create")
    
            if submitted:
                if not st.session_state.new_user_email or not st.session_state.new_user_role:
                    st.warning("⚠️ Please fill in both email and role.")
                else:
                    message = register_user(st.session_state.new_user_email, st.session_state.new_user_role)
                    placeholder = st.empty()
                    placeholder.success(f"✅ {message}")
                    time.sleep(1)
                    placeholder.empty()
    
                    # Clear form fields
                    st.session_state.new_user_email = ""
                    st.session_state.new_user_role = ""
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

                is_admin_email = email == "admin@theincubatorhub.com"

                display_users.append({
                    "index": i,
                    "userid": user.get("userid"),
                    "email": user.get("email"),
                    "role": user.get("role"),
                    "status": status,
                    "must_change_password": "N/A" if is_admin_email else user.get("must_change_password"),
                    "profile_completed": "N/A" if is_admin_email else user.get("profile_completed"),
                    "created_at": format_datetime(user.get("created_at")) if user.get("created_at") else "-"
                })

            st.markdown("#### User Table")

            st.markdown("""
            <style>
            .scrollable-table-container {
                overflow-x: auto;
                width: 100%;
            }
            .user-table {
                min-width: 900px;
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed;
            }
            .user-table th, .user-table td {
                border: 1px solid #ccc;
                padding: 8px 6px;
                text-align: left;
                vertical-align: middle;
                word-wrap: break-word;
                white-space: nowrap;
                font-size: 0.9rem;
            }
            .user-table th {
                background-color: #f5f5f5;
            }
            </style>
            """, unsafe_allow_html=True)

            st.markdown('<div class="scrollable-table-container">', unsafe_allow_html=True)
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

            for user in display_users:
                cols = st.columns([0.3, 2.2, 1.5, 1.2, 1.2, 2.5, 1.5, 1])
                cols[0].markdown(f"{user['index']}")
                cols[1].markdown(user["email"])
                cols[2].markdown(user["role"])
                cols[3].markdown(str(user["must_change_password"]))
                cols[4].markdown(str(user["profile_completed"]))
                cols[5].markdown(user["created_at"])

                if user["role"] == "Admin":
                    cols[6].markdown("N/A")
                    cols[7].markdown("🚫")
                else:
                    new_status = cols[6].selectbox(
                        "", ["Active", "Inactive", "Delete"],
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

            st.markdown("</table></div>", unsafe_allow_html=True)
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
                - Date: {format_datetime(s['date']) if s.get('date') else 'Unknown'}
                - Rating: {s.get('rating', '-') if s.get('rating') else '-'}
                """)
        else:
            st.info("No sessions found.")
