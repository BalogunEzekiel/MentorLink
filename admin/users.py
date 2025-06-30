# mentorlinks/admin/users.py
import streamlit as st
from database import supabase
from utils.helpers import format_datetime

ADMIN_EMAIL = "admin@theincubatorhub.com"

def show_users_tab():
    st.subheader("All Users")
    try:
        users = supabase.table("users").select("""
            userid, email, role, must_change_password, profile_completed, created_at, status
        """).neq("status", "Delete").execute().data
    except Exception as e:
        st.error(f"Failed to load users: {e}")
        return

    if not users:
        st.info("No users found.")
        return

    email_filter = st.text_input("Search by Email").lower()
    status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive"])

    for i, user in enumerate(users, start=1):
        email = user["email"].lower()
        status = user.get("status", "Active")
        if email_filter and email_filter not in email:
            continue
        if status_filter != "All" and status != status_filter:
            continue

        user_id = user["userid"]
        is_admin = email == ADMIN_EMAIL

        cols = st.columns([0.3, 2.2, 1.5, 1.2, 1.2, 2.5, 1.5, 1])
        cols[0].markdown(f"{i}")
        cols[1].markdown(user["email"])
        cols[2].markdown(user["role"])
        cols[3].markdown("N/A" if is_admin else str(user["must_change_password"]))
        cols[4].markdown("N/A" if is_admin else str(user["profile_completed"]))
        cols[5].markdown(format_datetime(user.get("created_at")))

        if is_admin:
            cols[6].markdown("N/A")
            cols[7].markdown("🚫")
        else:
            new_status = cols[6].selectbox("", ["Active", "Inactive", "Delete"],
                                           index=["Active", "Inactive", "Delete"].index(status),
                                           key=f"status_{user_id}")
            confirm = cols[6].checkbox("⚠️ Confirm", key=f"confirm_{user_id}") if new_status == "Delete" else True

            if cols[7].button("Update", key=f"btn_{user_id}") and confirm:
                try:
                    if new_status == "Delete":
                        supabase.table("users").delete().eq("userid", user_id).execute()
                        st.success(f"🗑️ Deleted {email}")
                    else:
                        supabase.table("users").update({"status": new_status}).eq("userid", user_id).execute()
                        st.success(f"🔁 Updated {email} to {new_status}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error updating user: {e}")
