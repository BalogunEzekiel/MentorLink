import streamlit as st
from datetime import datetime, timedelta
from database import supabase
from utils.helpers import format_datetime
from mentor_calendar import show_calendar
from postgrest.exceptions import APIError

def show():
    st.title("Mentor Dashboard")
    st.info("View mentorship requests, manage availability, upload your profile photo, and see upcoming sessions.")

    if "user" not in st.session_state:
        st.error("Please log in first.")
        return

    user = st.session_state.user
    mentor_id = user.get("userid")

    if not mentor_id:
        st.error("Mentor ID not found.")
        return

    # ✅ Profile Picture Section
    st.subheader("👤 Profile Picture")

    # Fetch profile data
    profile = supabase.table("profile").select("profile_image_url").eq("userid", mentor_id).single().execute().data
    current_image = profile.get("profile_image_url") if profile and profile.get("profile_image_url") else None

    if current_image:
        st.image(current_image, width=150, caption="Your Profile Picture")
    else:
        st.image("https://ui-avatars.com/api/?name=Mentor&background=cccccc&color=333333", width=150, caption="Default")

    uploaded_file = st.file_uploader("Upload new profile picture", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        try:
            # Upload to Supabase Storage
            path = f"profile_images/{mentor_id}_{uploaded_file.name}"
            supabase.storage.from_("avatars").upload(path, uploaded_file, {"upsert": True})
            public_url = supabase.storage.from_("avatars").get_public_url(path)

            # Update or insert into profile table
            supabase.table("profile").upsert({
                "userid": mentor_id,
                "profile_image_url": public_url
            }).execute()

            st.success("✅ Profile picture uploaded successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")

    # ✅ Tabs for Requests, Sessions, Calendar
    tabs = st.tabs(["📥 Requests", "📅 Sessions", "🗓 Calendar"])

    # 📥 Mentorship Requests
    with tabs[0]:
        st.subheader("Incoming Mentorship Requests")
        try:
            requests = supabase.table("mentorshiprequest") \
                .select("*") \
                .eq("mentorid", mentor_id) \
                .eq("status", "PENDING") \
                .execute().data
        except APIError as e:
            st.error("Failed to fetch mentorship requests.")
            st.code(str(e), language="json")
            return

        if requests:
            mentee_ids = list({r["menteeid"] for r in requests if r.get("menteeid")})

            try:
                mentees = supabase.table("users") \
                    .select("userid, email") \
                    .in_("userid", mentee_ids) \
                    .execute().data
                mentee_lookup = {m["userid"]: m["email"] for m in mentees}
            except APIError as e:
                st.error("Failed to fetch mentee details.")
                st.code(str(e), language="json")
                return

            for req in requests:
                mentee_email = mentee_lookup.get(req["menteeid"], "Unknown")
                st.markdown(f"**From:** {mentee_email}")
                col1, col2 = st.columns(2)

                if col1.button("Accept", key=f"accept_{req['mentorshiprequestid']}"):
                    try:
                        supabase.table("mentorshiprequest").update({"status": "ACCEPTED"}) \
                            .eq("mentorshiprequestid", req["mentorshiprequestid"]).execute()

                        session_date = (datetime.now() + timedelta(days=1)).isoformat()
                        supabase.table("session").insert({
                            "mentorid": req["mentorid"],
                            "menteeid": req["menteeid"],
                            "date": session_date,
                            "mentorshiprequestid": req["mentorshiprequestid"]
                        }).execute()

                        st.success(f"✅ Accepted request from {mentee_email} and scheduled session.")
                        st.rerun()
                    except APIError as e:
                        st.error("Failed to accept request.")
                        st.code(str(e), language="json")

                if col2.button("Reject", key=f"reject_{req['mentorshiprequestid']}"):
                    try:
                        supabase.table("mentorshiprequest").update({"status": "REJECTED"}) \
                            .eq("mentorshiprequestid", req["mentorshiprequestid"]).execute()
                        st.warning(f"❌ Rejected request from {mentee_email}")
                        st.rerun()
                    except APIError as e:
                        st.error("Failed to reject request.")
                        st.code(str(e), language="json")
        else:
            st.info("No pending requests.")

    # 📅 Sessions
    with tabs[1]:
        st.subheader("Scheduled Sessions")
        try:
            sessions = supabase.table("session").select("*") \
                .eq("mentorid", mentor_id) \
                .order("date", desc=False).execute().data
        except APIError as e:
            st.error("Failed to fetch sessions.")
            st.code(str(e), language="json")
            return

        if sessions:
            mentee_ids = list({s["menteeid"] for s in sessions if s.get("menteeid")})
            try:
                mentees = supabase.table("users").select("userid, email") \
                    .in_("userid", mentee_ids).execute().data
                mentee_lookup = {m["userid"]: m["email"] for m in mentees}
            except APIError as e:
                st.error("Failed to fetch mentee details.")
                st.code(str(e), language="json")
                return

            for s in sessions:
                mentee_email = mentee_lookup.get(s["menteeid"], "Unknown")
                st.markdown(f"""
                #### Session with {mentee_email}
                - 🗓 **Date:** {format_datetime(s['date'])}
                - ⭐ **Rating:** {s.get('rating', 'Pending')}
                - 💬 **Feedback:** {s.get('feedback', 'Not submitted yet')}
                """)
        else:
            st.info("No upcoming or past sessions yet.")

    # 🗓 Calendar
    with tabs[2]:
        st.subheader("Visual Schedule")
        show_calendar()
