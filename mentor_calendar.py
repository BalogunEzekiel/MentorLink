import plotly.express as px
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from database import supabase

def show_calendar():
    if "user" not in st.session_state:
        st.warning("Please log in to view your calendar.")
        return

    user = st.session_state["user"]
    mentor_id = user.get("userid")

    if not mentor_id:
        st.error("Mentor ID not found.")
        return

    tabs = st.tabs(["📅 My Sessions", "🗓️ Set Availability"])

    # 📅 My Sessions Tab
    with tabs[0]:
        st.subheader("📅 Scheduled Sessions")

        # Filter sessions by mentor_id and status 'accepted'
        response = supabase.table("session") \
            .select("*, users!session_menteeid_fkey(email)") \
            .eq("mentorid", mentor_id) \
            .eq("status", "accepted") \
            .execute()

        sessions = response.data

        if not sessions:
            st.info("No upcoming or past sessions yet.")
            return

        df = pd.DataFrame([{
            "Session ID": s["sessionid"],
            "Session With": s["users"]["email"],
            "Start": pd.to_datetime(s["date"]),
            "End": pd.to_datetime(s["date"]) + timedelta(hours=1),
            "Feedback": s.get("feedback", ""),
            "Rating": s.get("rating", "Pending")
        } for s in sessions])

        # Plot timeline
        fig = px.timeline(df, x_start="Start", x_end="End", y="Session With", color="Rating",
                          hover_data=["Feedback", "Rating"])
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(title="Mentor Session Calendar", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

        # Session details dropdown
        session_options = {f"{row['Session With']} @ {row['Start']}": row for _, row in df.iterrows()}
        selected_label = st.selectbox("📂 View Session Details", list(session_options.keys()))
        selected_row = session_options[selected_label]

        st.markdown(f"""
        ### 📝 Session Details
        - 👤 **Mentee**: {selected_row['Session With']}
        - 🗓️ **Start Time**: {selected_row['Start']}
        - 🕒 **End Time**: {selected_row['End']}
        - ⭐ **Rating**: {selected_row['Rating']}
        - 💬 **Feedback**: {selected_row['Feedback'] or 'Not provided'}
        """)

    # 🗓️ Set Availability Tab (unchanged)
    with tabs[1]:
        st.subheader("🗓️ Add Your Availability")
        with st.form("availability_form"):
            date = st.date_input("Select a date")
            start_time = st.time_input("Start time")
            end_time = st.time_input("End time")
            submitted = st.form_submit_button("Submit Availability")

            if submitted:
                start_datetime = datetime.combine(date, start_time)
                end_datetime = datetime.combine(date, end_time)
                if end_datetime <= start_datetime:
                    st.error("❌ End time must be after start time.")
                else:
                    try:
                        supabase.table("mentoravailability").insert({
                            "mentorid": mentor_id,
                            "start_time": start_datetime.isoformat(),
                            "end_time": end_datetime.isoformat()
                        }).execute()
                        st.success("✅ Availability set successfully!")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error("❌ Failed to set availability.")
                        st.exception(e)

        # View existing availability
        st.markdown("### 📋 Your Availability")
        try:
            result = supabase.table("mentoravailability") \
                .select("*") \
                .eq("mentorid", mentor_id) \
                .order("start_time").execute()
            availability = result.data
            if availability:
                availability_df = pd.DataFrame([{
                    "Start": pd.to_datetime(a["start_time"]),
                    "End": pd.to_datetime(a["end_time"])
                } for a in availability])
                st.dataframe(availability_df, use_container_width=True)
            else:
                st.info("ℹ️ You haven’t set any availability yet.")
        except Exception as e:
            st.error("🚫 Error fetching availability.")
            st.exception(e)
