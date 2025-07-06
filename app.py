import streamlit as st
import sys
import os

# ✅ Ensure local module imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ✅ Import local components
from components.landing_page import show_landing
from utils.setup_admin import setup_admin_account
from utils.auto_cancel import cancel_expired_requests
from auth.auth_handler import login, logout
from auth.profile import change_password, profile_form
from components.sidebar import sidebar
from components.mentorchat_widget import mentorchat_widget
from roles import admin, mentor, mentee
from utils.footer import app_footer

# ✅ Set app configuration
st.set_page_config(page_title="MentorLink", layout="wide")

# ✅ Custom header
st.markdown("""
    <style>
    @font-face {
        font-family: 'ScriptMTBold';
        src: local("Script MT Bold");
    }

    /* Fixed header */
    .custom-header-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        z-index: 9999;
        background-color: white;
        padding: 0rem 1rem;
        border-bottom: 2px solid #ccc;
    }

    .custom-header {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        font-family: 'ScriptMTBold', cursive, serif;
        font-size: 70px;
        color: #4B8BBE;
        font-weight: bold;
        margin: -2;
        line-height: 0;
        word-wrap: break-word;
    }

    .custom-header img {
        height: 140px;
        margin-top: 0px;
    }

    /* Push content down */
    .main .block-container {
        padding-top: 2rem !important;
    }

    header[data-testid="stHeader"] {
        background-color: transparent;
    }
    </style>

    <div class='custom-header-container'>
        <div class='custom-header'>
            <img src="https://fzmmeysjrltnktlfkhye.supabase.co/storage/v1/object/public/public-assets//mentorlink_logo.png" alt="MentorLink Logo">
            MentorLink
        </div>
    </div>
""", unsafe_allow_html=True)

# ✅ Setup and initialize
setup_admin_account()
cancel_expired_requests()
sidebar()
mentorchat_widget()

# ✅ Auth & Routing Logic
if not st.session_state.get("authenticated", False):
    login()
    show_landing()
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

# ✅ Footer for unauthenticated users
if not st.session_state.get("authenticated", False):
    app_footer()

# 🔁 Optional rerun trigger
if st.session_state.get("do_rerun"):
    st.session_state["do_rerun"] = False
    st.rerun()
