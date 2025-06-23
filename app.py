
import streamlit as st
from auth import login, logout, register, get_user_role
from roles import admin, mentor, mentee

st.set_page_config(page_title="Mentorship Platform", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    action = st.sidebar.radio("Choose", ["Login", "Register"])
    if action == "Login":
        login()
    else:
        register()
else:
    role = get_user_role()
    st.sidebar.button("Logout", on_click=logout)
    if role == "Admin":
        admin.show()
    elif role == "Mentor":
        mentor.show()
    elif role == "Mentee":
        mentee.show()
