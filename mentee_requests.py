import streamlit as st
from datetime import datetime
import pandas as pd
from database import supabase
import pytz

def show():
    st.subheader("📬 Mentorship Requests & Booking")

    if "user" not in st.session_state:
        st.warning("Please log in first.")
        return

    user = st.session_state["user"]
    menteeid = user.get("userid")
    lagos_tz = pytz.timezone("Africa/Lagos")

    # Step 1: Fetch accepted mentorship requests
    accepted_requests = supabase.table("mentorshiprequest") \
        .select("*, users!mentorshiprequest_mentorid_fkey(email)") \
        .eq("menteeid", menteeid) \
        .eq("status", "ACCEPTED") \
        .execute().data

    if not accepted_requests:
        st.info("No accepted mentorship requests.")
        return

    st.markdown("##### ✅ Accepted Requests (Book a Session)")
    for req in accepted_requests:
        mentor_email = req["users"]["email"]
        st.markdown(f"#### Mentor: {mentor_email}")

        # Step 2: Get mentor's available slots
        slots = supabase.table("availability") \
            .select("*") \
            .eq("mentorid", req["mentorid"]) \
            .order("start") \
            .execute().data

        if not slots:
            st.info("No available slots for this mentor yet.")
            continue

        # Format slot options nicely
        slot_options = {}
        for s in slots:
            start_dt = pd.to_datetime(s["start"]).tz_localize("UTC").astimezone(lagos_tz)
            end_dt = pd.to_datetime(s["end"]).tz_localize("UTC").astimezone(lagos_tz)
            label = f"{start_dt.strftime('%a, %d %b %Y %I:%M %p')} ➡ {end_dt.strftime('%I:%M %p')}"
            slot_options[label] = s

        selected_label = st.selectbox(
            f"📅 Choose a time slot with {mentor_email}",
            list(slot_options.keys()),
            key=f"slot_{req['mentorshiprequestid']}"
        )

        if st.button("📌 Book This Slot", key=f"book_{req['mentorshiprequestid']}"):
            selected_slot = slot_options[selected_label]
            try:
                # Prevent double booking: check if the slot is still available
                exists = supabase.table("session") \
                    .select("sessionid") \
                    .eq("mentorid", req["mentorid"]) \
                    .eq("date", selected_slot["start"]) \
                    .execute().data

                if exists:
                    st.warning("⚠️ This slot has just been booked by someone else.")
                    st.rerun()
                    return

                # Step 3: Create the session
                supabase.table("session").insert({
                    "mentorid": req["mentorid"],
                    "menteeid": req["menteeid"],
                    "date": selected_slot["start"],
                    "end_time": selected_slot["end"],
                    "mentorshiprequestid": req["mentorshiprequestid"],
                    "feedback": "",
                    "rating": None,
                    "status": "Scheduled"
                }).execute()

                # Optional: Remove the slot after booking
                supabase.table("availability") \
                    .delete().eq("availabilityid", selected_slot["availabilityid"]).execute()

                st.success(f"✅ Session booked successfully with {mentor_email}!")
                st.rerun()

            except Exception as e:
                st.error("❌ Failed to book the session.")
                st.exception(e)
