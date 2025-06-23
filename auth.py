# Handles login, register, session state, and Supabase auth integration
import streamlit as st
from supabase import create_client, Client
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def login():
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if not email or not password:
            st.warning("Please enter both email and password.")
            return
        result = supabase.table("users").select("*").eq("email", email).execute()
        if result.data:
            user = result.data[0]
            if bcrypt.checkpw(password.encode(), user["password"].encode()):
                st.session_state.authenticated = True
                st.session_state.user = user
                st.session_state.role = user["role"]
                st.success(f"Welcome, {user['email']}!")
                st.experimental_rerun()
            else:
                st.error("Incorrect password.")
        else:
            st.error("User not found.")

def register():
    st.title("Register")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["Mentee", "Mentor"])
    if st.button("Register"):
        if not email or not password:
            st.warning("Please provide an email and password.")
            return
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        try:
            result = supabase.table("users").insert({
                "email": email,
                "password": hashed_pw,
                "role": role
            }).execute()
            st.success("Registered successfully! You can now login.")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error: {e}")

def logout():
    st.session_state.clear()
    st.success("Logged out.")
    st.experimental_rerun()

def get_user_role():
    return st.session_state.get("role", None)
