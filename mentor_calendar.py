import plotly.express as px
import pandas as pd
from database import supabase
import streamlit as st

def show_calendar():
    if "user" not in st.session_state:
        st.warning("Please log in to view your calendar.")
        return

    user = st.session_state["user"]
    mentor_id = user.get("userid")

    if not mentor_id:
        st.error("Mentor ID not found.")
        return

    st.write(f"Mentor calendar for user ID: {mentor_id}")

    # Fetch sessions from Supabase
    response = supabase.table("session") \
        .select("*, users!session_menteeid_fkey(email)") \
        .eq("mentorid", mentor_id) \
        .execute()

    sessions = response.data

    if not sessions:
        st.warning("No sessions to display.")
        return

    # Create DataFrame for visualization
    df = pd.DataFrame([{
        "Session With": s["users"]["email"],
        "Start": s["date"],
        "End": s["date"],  # Assuming session is instantaneous
        "Feedback": s.get("feedback", ""),
        "Rating": s.get("rating", "")
    } for s in sessions])

    # Plot timeline
    fig = px.timeline(df, x_start="Start", x_end="End", y="Session With", color="Rating")
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)
