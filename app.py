
import streamlit as st
from auth import login, logout, register, get_user_role
from roles import admin, mentor, mentee

st.set_page_config(page_title="MentorLink", layout="wide")

from auth import login, logout, change_password, profile_form

if not st.session_state.get("authenticated", False):
    login()
elif st.session_state.get("force_change_password", False):
    change_password()
elif st.session_state.get("force_profile_update", False):
    profile_form()
else:
    role = st.session_state.get("role")
    st.sidebar.button("Logout", on_click=logout)

    if role == "Admin":
        admin.show()
    elif role == "Mentor":
        mentor.show()
    elif role == "Mentee":
        mentee.show()

if st.session_state.get("do_rerun"):
    del st.session_state["do_rerun"]  # clean up
    st.rerun()
