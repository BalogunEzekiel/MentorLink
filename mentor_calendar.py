import plotly.express as px
import pandas as pd
from database import supabase
import streamlit as st

def show_calendar():
    mentor_id = st.session_state.user["userid"]
    sessions = supabase.table("session") \
        .select("*, users!session_menteeid_fkey(email)") \
        .eq("mentorid", mentor_id).execute().data

    if not sessions:
        st.warning("No sessions to display.")
        return

    df = pd.DataFrame([{
        "Session With": s["users"]["email"],
        "Start": s["date"],
        "End": s["date"],  # assuming single point session
        "Feedback": s.get("feedback", ""),
        "Rating": s.get("rating", "")
    } for s in sessions])

    fig = px.timeline(df, x_start="Start", x_end="End", y="Session With", color="Rating")
    fig.update_yaxes(autorange="reversed")  # Optional
    st.plotly_chart(fig, use_container_width=True)
