# Forms for profile creation and validation
import streamlit as st

def profile_form():
    bio = st.text_area("Short Bio")
    skills = st.multiselect("Skills", ["Marketing", "UI/UX", "Web Dev", "Data Science"])
    goals = st.text_input("Your goal (e.g., 'Improve leadership')")
    return {"bio": bio, "skills": ", ".join(skills), "goals": goals}
