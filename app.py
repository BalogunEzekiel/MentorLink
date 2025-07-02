import streamlit as st
import sys
import os

# ✅ Ensure local module imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ✅ Set app configuration
st.set_page_config(page_title="MentorLink", layout="wide")

# ✅ Custom header and GLOBAL CSS for MentorLink public section
# All the CSS for .mentorlink-public, .story-section, etc., is now here
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

    /* CSS moved from landing_page.py to app.py for global application */
    .mentorlink-public .story-section {
        background-color: #f7f9fc;
        padding: 2rem 1rem;
        border-radius: 10px;
        margin-top: 2rem;
    }
    .mentorlink-public .story-container {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: center;
    }
    .mentorlink-public .story-card {
        background-color: white;
        flex: 1;
        min-width: 300px;
        max-width: 400px;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    .mentorlink-public .story-card h3 {
        color: #4B8BBE;
        font-size: 1.3rem;
    }
    .mentorlink-public .story-card p {
        line-height: 1.6;
        font-size: 0.95rem;
    }
    .mentorlink-public .hero-image {
        width: 100%;
        border-radius: 10px;
        max-height: 300px;
        object-fit: cover;
        margin-bottom: 1.5rem;
    }
    @media (max-width: 768px) {
        .mentorlink-public .story-container {
            flex-direction: column;
        }
    }
    </style>
    <div class='custom-header'>MentorLink</div>
    <hr style='margin: 0.2rem 0 0.5rem 0;'>
""", unsafe_allow_html=True)

# ✅ Import core app logic
from utils.setup_admin import setup_admin_account
from utils.auto_cancel import cancel_expired_requests
from auth.auth_handler import login, logout
from auth.profile import change_password, profile_form
from components.sidebar import sidebar
from components.mentorchat_widget import mentorchat_widget
from components.landing_page import show_landing # This still imports the function
from roles import admin, mentor, mentee
from utils.footer import app_footer

# ✅ Initialization
setup_admin_account()
cancel_expired_requests()
sidebar()
mentorchat_widget()

# ✅ Auth & Routing
if not st.session_state.get("authenticated", False):
    login()
    show_landing()  # ✅ Modular public landing page
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

# ✅ Footer for public page
if not st.session_state.get("authenticated", False):
    app_footer()

# 🔁 Optional rerun trigger
if st.session_state.get("do_rerun"):
    st.session_state["do_rerun"] = False
    st.rerun()
