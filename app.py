import streamlit as st
import sys
import os

# ✅ Ensure local module imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ✅ Set app configuration
st.set_page_config(page_title="MentorLink", layout="wide")

# ✅ Custom header
st.markdown("""
    <style>
    @font-face {
        font-family: 'ScriptMTBold';
        src: local("Script MT Bold");
    }
    .custom-header {
        font-family: 'ScriptMTBold', cursive, serif;
        font-size: 80px;
        color: #4B8BBE;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.1rem;
        margin-top: -1rem;
    }
    .block-container {
        padding-top: 0.5rem !important;
    }
    </style>
    <div class='custom-header'>MentorLink</div>
    <hr style='margin: 0.2rem 0 0.5rem 0;'>
""", unsafe_allow_html=True)

# ✅ Initial setup
from utils.setup_admin import setup_admin_account
from utils.auto_cancel import cancel_expired_requests
setup_admin_account()
cancel_expired_requests()

# ✅ Imports
from auth.auth_handler import login
from auth.profile import change_password, profile_form
from components.sidebar import sidebar
from components.landing_page import show_landing
from components.mentorchat_widget import mentorchat_widget
from utils.footer import app_footer
from roles import admin, mentor, mentee

# ✅ Always show sidebar and chat
sidebar()
mentorchat_widget()

# ✅ Routing logic
if not st.session_state.get("authenticated", False):
    login()
    show_landing()
    app_footer()
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

# ✅ Handle rerun
if st.session_state.get("do_rerun"):
    st.session_state["do_rerun"] = False
    st.rerun()
