import streamlit as st
import sys
import os

# Ensure local module imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup admin account on first run
from utils.setup_admin import setup_admin_account
setup_admin_account()

# Import views and handlers
from auth.auth_handler import login, logout
from auth.profile import change_password, profile_form
from components.sidebar import sidebar
from roles import admin, mentor, mentee
from utils.footer import app_footer

# Set app configuration
st.set_page_config(page_title="MentorLink", layout="wide")

# Always show sidebar
sidebar()

# Main logic
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

# ✅ Show footer only if user is NOT authenticated
if not st.session_state.get("authenticated", False):
    app_footer()

# ✅ Optional rerun handling
if st.session_state.get("do_rerun"):
    st.session_state["do_rerun"] = False
    st.rerun()
