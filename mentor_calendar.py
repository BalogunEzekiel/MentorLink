import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from database import supabase
import pytz
import plotly.express as px

def show_calendar():
    st.subheader("🗓️ Mentor Calendar")

    if "user" not in st.session_state:
        st.warning("Please log in to view your calendar.")
        return

    user = st.session_state["user"]
    mentorid = user.get("userid")
    lagos_tz = pytz.timezone("Africa/Lagos")

    if not mentorid:
        st.error("Mentor ID not found.")
        return

    tabs = st.tabs(["📅 My Sessions", "🗓️ Set Availability"])

    # ---------------------- 📅 My Sessions Tab ----------------------
    with tabs[0]:
        st.subheader("📅 Scheduled Sessions")

        try:
            response = supabase.table("session") \
                .select("*, users!session_menteeid_fkey(email), mentorshiprequest!session_mentorshiprequestid_fkey(status)") \
                .eq("mentorid", mentorid) \
                .order("date") \
                .execute()

            all_sessions = response.data or []

            # Filter for sessions where mentorshiprequest status is ACCEPTED
            sessions = [
                s for s in all_sessions
                if s.get("mentorshiprequest", {}).get("status") == "ACCEPTED"
            ]

            if not sessions:
                st.info("No upcoming or past sessions yet.")
                return

            df = pd.DataFrame([{
                "Session ID": s["sessionid"],
                "Session With": s.get("users", {}).get("email", "Unknown"),
                "Start": pd.to_datetime(s["date"]).tz_localize("UTC").astimezone(lagos_tz),
                "End": pd.to_datetime(s["date"]).tz_localize("UTC").astimezone(lagos_tz) + timedelta(hours=1),
                "Feedback": s.get("feedback", ""),
                "Rating": s.get("rating", "Pending")
            } for s in sessions])

            # Plot timeline chart for sessions
            fig = px.timeline(
                df,
                x_start="Start",
                x_end="End",
                y="Session With",
                color="Rating",
                hover_data=["Feedback", "Rating"]
            )
            fig.update_yaxes(autorange="reversed")
            fig.update_layout(
                title="Mentor Session Calendar",
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

            # Session details dropdown
            session_options = {
                f"{row['Session With']} @ {row['Start'].strftime('%a, %d %b %Y %I:%M %p')}": row
                for _, row in df.iterrows()
            }

            selected_label = st.selectbox("📂 View Session Details", list(session_options.keys()))
            selected_row = session_options[selected_label]

            st.markdown(f"""
            ### 📝 Session Details
            - 👤 **Mentee**: {selected_row['Session With']}
            - 🗓️ **Start Time**: {selected_row['Start'].strftime('%A, %d %B %Y %I:%M %p')}
            - 🕒 **End Time**: {selected_row['End'].strftime('%I:%M %p')}
            - ⭐ **Rating**: {selected_row['Rating']}
            - 💬 **Feedback**: {selected_row['Feedback'] or 'Not provided'}
            """)

        except Exception as e:
            st.error("🚫 Failed to load sessions.")
            st.exception(e)

    # ---------------------- 🗓️ Set Availability Tab ----------------------
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
                        # Check for overlapping slots
                        existing_slots = supabase.table("availability") \
                            .select("*") \
                            .eq("mentorid", mentorid) \
                            .execute().data or []

                        has_overlap = any(
                            not (
                                end_datetime <= pd.to_datetime(slot["start"]) or
                                start_datetime >= pd.to_datetime(slot["end"])
                            )
                            for slot in existing_slots
                        )

                        if has_overlap:
                            st.error("❌ This time slot overlaps with an existing one.")
                        else:
                            supabase.table("availability").insert({
                                "mentorid": mentorid,
                                "start": start_datetime.isoformat(),
                                "end": end_datetime.isoformat()
                            }).execute()
                            st.success("✅ Availability set successfully!")
                            st.rerun()

                    except Exception as e:
                        st.error("❌ Failed to set availability.")
                        st.exception(e)

        # Show existing availability
        st.markdown("### 📋 Your Availability")
        try:
            result = supabase.table("availability") \
                .select("*") \
                .eq("mentorid", mentorid) \
                .order("start") \
                .execute()

            availability = result.data or []

            if availability:
                availability_df = pd.DataFrame([{
                    "Start": pd.to_datetime(a["start"]).tz_localize("UTC").astimezone(lagos_tz),
                    "End": pd.to_datetime(a["end"]).tz_localize("UTC").astimezone(lagos_tz)
                } for a in availability])
                st.dataframe(availability_df, use_container_width=True)
            else:
                st.info("ℹ️ You haven’t set any availability yet.")
        except Exception as e:
            st.error("🚫 Error fetching availability.")
            st.exception(e)
