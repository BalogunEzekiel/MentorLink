import streamlit as st
import sys
import os
from datetime import datetime, timedelta, timezone

# Ensure local module imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ✅ Set app configuration
st.set_page_config(page_title="MentorLink", layout="wide")

# ✅ Setup admin on first run
from utils.setup_admin import setup_admin_account
setup_admin_account()

from utils.auto_cancel import cancel_expired_requests
cancel_expired_requests()

# ✅ Auto-cancel stale mentorship requests after 48 hours
from database import supabase

def cancel_expired_requests():
    try:
        response = supabase.table("mentorshiprequest") \
            .select("mentorshiprequestid, createdat, status") \
            .eq("status", "PENDING") \
            .execute()

        now = datetime.now(timezone.utc)
        for req in response.data:
            createdat = datetime.fromisoformat(req["createdat"])
            if now - createdat > timedelta(hours=48):
                supabase.table("mentorshiprequest") \
                    .update({"status": "CANCELLED_AUTO"}) \
                    .eq("id", req["mentorshiprequestid"]).execute()
    except Exception as e:
        st.error(f"⚠️ Failed to auto-cancel expired requests: {e}")

cancel_expired_requests()

# ✅ Import views and handlers
from auth.auth_handler import login, logout
from auth.profile import change_password, profile_form
from components.sidebar import sidebar
from roles import admin, mentor, mentee
from utils.footer import app_footer
from components.mentorchat_widget import mentorchat_widget  # ✅ floating chat widget

# ✅ Always show sidebar
sidebar()

# ✅ Show floating chat on every page if toggled
mentorchat_widget()

# 🔐 Auth + Routing
if not st.session_state.get("authenticated", False):
    login()
else:
    role = st.session_state.get("role")
    user = st.session_state.get("user", {})

    if role != "Admin":
        if user.get("must_change_password", False):
            change_password()
        elif not user.get("profile_completed", False):
            profile_form()
        else:
            if role == "Mentor":
                mentor.show()
            elif role == "Mentee":
                mentee.show()
            else:
                st.warning("⚠️ Unknown role.")
    else:
        admin.show()

# 🧾 Show footer only if not logged in
if not st.session_state.get("authenticated", False):
    app_footer()

# 🔁 Handle rerun flags
if st.session_state.get("do_rerun"):
    st.session_state["do_rerun"] = False
    st.rerun()
