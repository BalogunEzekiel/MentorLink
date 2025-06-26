import plotly.express as px
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from database import supabase

def show_calendar():
    st.subheader("🗓️ Mentor Calendar")

    if "user" not in st.session_state:
        st.warning("Please log in to view your calendar.")
        return

    user = st.session_state["user"]
    mentorid = user.get("userid")

    if not mentorid:
        st.error("Mentor ID not found.")
        return

    tabs = st.tabs(["📅 My Sessions", "🗓️ Set Availability"])

    # 📅 My Sessions Tab
    with tabs[0]:
        st.subheader("📅 Scheduled Sessions")

        try:
            response = supabase.table("session") \
                .select("*, users!session_menteeid_fkey(email), mentorshiprequest!session_mentorshiprequestid_fkey(status)") \
                .eq("mentorid", mentorid) \
                .order("date") \
                .execute()

            all_sessions = response.data

            # ✅ Filter sessions where mentorship request is ACCEPTED
            sessions = [s for s in all_sessions if s.get("mentorshiprequest", {}).get("status") == "ACCEPTED"]

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

            # 📊 Timeline Chart
            fig = px.timeline(df, x_start="Start", x_end="End", y="Session With", color="Rating",
                              hover_data=["Feedback", "Rating"])
            fig.update_yaxes(autorange="reversed")
            fig.update_layout(title="Mentor Session Calendar", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)

            # 🔍 Session Details Dropdown
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
        except Exception as e:
            st.error("🚫 Failed to load sessions.")
            st.exception(e)

    # 🗓️ Set Availability Tab
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
                    # ✅ Check for overlap before inserting
                    overlap_check = supabase.table("availability") \
                        .select("*") \
                        .eq("mentorid", mentorid) \
                        .execute()

                    existing_slots = overlap_check.data or []

                    has_overlap = any(
                        not (end_datetime <= pd.to_datetime(slot["start"]) or start_datetime >= pd.to_datetime(slot["end"]))
                        for slot in existing_slots
                    )

                    if has_overlap:
                        st.error("❌ This time slot overlaps with existing availability. Please choose a different time.")
                    else:
                        try:
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

        # 📋 List Availability
        st.markdown("### 📋 Your Availability")
        try:
            result = supabase.table("availability") \
                .select("*") \
                .eq("mentorid", mentorid) \
                .order("start") \
                .execute()

            availability = result.data
            if availability:
                availability_df = pd.DataFrame([{
                    "Start": pd.to_datetime(a["start"]),
                    "End": pd.to_datetime(a["end"])
                } for a in availability])
                st.dataframe(availability_df, use_container_width=True)
            else:
                st.info("ℹ️ You haven’t set any availability yet.")
        except Exception as e:
            st.error("🚫 Error fetching availability.")
            st.exception(e)
