import streamlit as st
from database import supabase

def show():
    st.subheader("🗖 All Sessions")
    sessions = supabase.table("session").select("""
        *,
        mentor:users!session_mentorid_fkey(email),
        mentee:users!session_menteeid_fkey(email)
    """).execute().data

    for s in sessions:
        link = s.get("meet_link")
        date = s.get("date","Unknown")
        st.markdown(f"- **{s['mentor']['email']} ➡ {s['mentee']['email']}** | {date} | [🖥️ Join Meet]({link})")
