import streamlit as st
from datetime import datetime
import pandas as pd
from database import supabase

def show():
    st.subheader("📬 Mentorship Requests & Booking")

    if "user" not in st.session_state:
        st.warning("Please log in first.")
        return

    user = st.session_state["user"]
    menteeid = user.get("userid")

    # Step 1: Fetch accepted mentorship requests
    accepted_requests = supabase.table("mentorshiprequest") \
        .select("*, users!mentorshiprequest_mentorid_fkey(email)") \
        .eq("menteeid", menteeid) \
        .eq("status", "ACCEPTED") \
        .execute().data

    if not accepted_requests:
        st.info("No accepted mentorship requests.")
        return

    st.markdown("### ✅ Accepted Requests (Book a Session)")
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

        slot_options = {
            f"{pd.to_datetime(s['start'])} to {pd.to_datetime(s['end'])}": s for s in slots
        }

        selected_slot_label = st.selectbox(
            f"📅 Choose a time slot with {mentor_email}",
            list(slot_options.keys()),
            key=f"slot_{req['mentorshiprequestid']}"
        )

        if st.button("📌 Book This Slot", key=f"book_{req['mentorshiprequestid']}"):
            selected_slot = slot_options[selected_slot_label]
            try:
                # Step 3: Create the session
                supabase.table("session").insert({
                    "mentorid": req["mentorid"],
                    "menteeid": req["menteeid"],
                    "date": selected_slot["start"],
                    "mentorshiprequestid": req["mentorshiprequestid"],
                    "feedback": "",
                    "rating": None
                }).execute()

                # Optional: Remove or mark the slot as booked
                supabase.table("availability") \
                    .delete().eq("availabilityid", selected_slot["availabilityid"]).execute()

                st.success(f"✅ Session booked with {mentor_email}!")
                st.rerun()
            except Exception as e:
                st.error("❌ Booking failed.")
                st.exception(e)
