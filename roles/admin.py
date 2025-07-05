import sys
import os
import time
from datetime import datetime
import streamlit as st
import pandas as pd
import pytz
import plotly.express as px

# Adjust path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import supabase
from auth.auth_handler import register_user
from utils.session_creator import create_session_if_available
from utils.helpers import format_datetime_safe  # Handles timezone-safe formatting

# Set West Africa Time
WAT = pytz.timezone("Africa/Lagos")

def format_datetime(dt):
    """Convert datetime string or object to WAT-formatted string."""
    if not dt:
        return "Unknown"
    if isinstance(dt, datetime):
        return dt.astimezone(WAT).strftime("%A, %d %B %Y at %I:%M %p")
    try:
        parsed = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        return parsed.astimezone(WAT).strftime("%A, %d %B %Y at %I:%M %p")
    except Exception:
        return str(dt)

def session_status_label(date_str):
    try:
        now = datetime.now(WAT)
        session_time = datetime.fromisoformat(date_str.replace("Z", "+00:00")).astimezone(WAT)
        if session_time.date() < now.date() or session_time < now:
            return "🟥 Past"
        elif session_time.date() == now.date() and abs((session_time - now).total_seconds()) < 3600:
            return "🟨 Ongoing"
        else:
            return "🟩 Upcoming"
    except:
        return "❓ Unknown"

def show():
    st.title("Admin Dashboard")
    st.info("Admin dashboard: manage users, mentorship matches, and sessions.")

    tabs = st.tabs(["👥 Users", "📩 Requests", "🔁 Matches", "🗓️ Sessions", "📊 Analytics"])

    # --- USERS TAB--
    with tabs[0]:
        st.subheader("Register New User")
    
        with st.form("register_user", clear_on_submit=True):
            user_email = st.text_input("User Email", placeholder="e.g. user@example.com")
            role = st.selectbox("Assign Role", ["Select a role", "Mentor", "Mentee"])
            submitted = st.form_submit_button("Create")
    
        if submitted:
            if not user_email or role == "Select a role":
                st.warning("⚠️ Please fill in both email and role.")
            else:
                register_user(user_email, role)
                st.success(f"✅ User '{user_email}' registered as {role}.")
                time.sleep(1)
                st.rerun()
    
        st.subheader("All Users")
    
        try:
            users = supabase.table("users").select("""
                userid, email, role, must_change_password, profile_completed, created_at, status
            """).neq("status", "Delete").execute().data
        except Exception as e:
            st.error(f"❌ Failed to load users: {e}")
            users = []
    
        if users:
            df = pd.DataFrame(users)
            df["created_at"] = df["created_at"].apply(format_datetime)
            df = df.rename(columns={
                "userid": "User ID",
                "email": "Email",
                "role": "Role",
                "must_change_password": "Must Change Password",
                "profile_completed": "Profile Completed",
                "created_at": "Created At",
                "status": "Status"
            })
    
            email_search = st.text_input("🔍 Search by Email", placeholder="e.g. johndoe@example.com").lower()
            status_filter = st.selectbox("📂 Filter by Status", ["All", "Active", "Inactive"])
    
            filtered_df = df.copy()
            if email_search:
                filtered_df = filtered_df[filtered_df["Email"].str.lower().str.contains(email_search)]
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df["Status"] == status_filter]
    
            st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)
    
            selected_email = st.selectbox(
                "✏️ Select User to Update",
                ["Select an email..."] + df["Email"].tolist()
            )
    
            new_status = st.selectbox(
                "🛠️ New Status",
                ["Select status...", "Active", "Inactive", "Delete"]
            )
    
            confirm_delete_1 = confirm_delete_2 = False
            if new_status == "Delete":
                st.warning("⚠️ Deleting a user is permanent. Please confirm below:")
                confirm_delete_1 = st.checkbox(
                    "I understand that deleting this user is permanent and cannot be undone.",
                    key="confirm_delete_1"
                )
                confirm_delete_2 = st.checkbox(
                    "Yes, I really want to delete this user.",
                    key="confirm_delete_2"
                )
    
            if st.button("✅ Update Status"):
                if selected_email == "Select an email..." or new_status == "Select status...":
                    st.warning("⚠️ Please select both a valid user and a status.")
                else:
                    user_row = df[df["Email"] == selected_email].iloc[0]
                    user_id = user_row["User ID"]
    
                    try:
                        if new_status == "Delete":
                            if confirm_delete_1 and confirm_delete_2:
                                supabase.table("users").delete().eq("userid", user_id).execute()
                                st.success(f"✅ Deleted user: {selected_email}")
                                st.rerun()
                            else:
                                st.warning("☑️ You must confirm both checkboxes to proceed with deletion.")
                        else:
                            supabase.table("users").update({"status": new_status}).eq("userid", user_id).execute()
                            st.success(f"✅ Updated {selected_email} to {new_status}")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to update user: {e}")
    
            # ✅ Promotion logic (only for Active Mentees with completed profiles)
            if selected_email != "Select an email...":
                user_row = df[df["Email"] == selected_email].iloc[0]
                current_role = user_row["Role"]
                current_status = user_row["Status"]
                profile_completed = user_row["Profile Completed"]
    
                if current_role == "Mentee":
                    if current_status == "Active" and profile_completed:
                        promote = st.checkbox("🚀 Promote this *Active Mentee* (Profile Completed) to Mentor")
                        if promote and st.button("✅ Promote to Mentor"):
                            try:
                                supabase.table("users").update({"role": "Mentor"}).eq("userid", user_row["User ID"]).execute()
                                st.success(f"✅ {selected_email} promoted to Mentor!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Failed to promote user: {e}")
                    else:
                        st.info("⚠️ Only *Active Mentees* with a **completed profile** can be promoted to Mentors.")
        else:
            st.info("No users found.")

    # Mentorship Requests
    with tabs[1]:
        st.subheader("Mentorship Requests")
        try:
            requests = supabase.table("mentorshiprequest").select("""
                *, mentee:users!mentorshiprequest_menteeid_fkey(email),
                   mentor:users!mentorshiprequest_mentorid_fkey(email)
            """).neq("status", "ACCEPTED").execute().data
        except Exception as e:
            st.error(f"❌ Could not fetch mentorship requests: {e}")
            requests = []

        if requests:
            for req in requests:
                mentee_email = req['mentee']['email']
                mentor_email = req['mentor']['email']
                status = req.get("status", "Unknown")
                st.markdown(f"""
                - 🧑 Mentee: **{mentee_email}**  
                - 🧑‍🏫 Mentor: **{mentor_email}**  
                - 📌 Status: **{status}**
                """)
        else:
            st.info("No mentorship requests found.")

    # Match Mentees to Mentors
    with tabs[2]:
        st.subheader("Match Mentee to Mentor")
        try:
            users = supabase.table("users").select("userid, email, role, status") \
                .neq("status", "Delete").execute().data or []
            mentees = [u for u in users if u["role"] == "Mentee"]
            mentors = [u for u in users if u["role"] == "Mentor"]
        except Exception as e:
            st.error(f"❌ Failed to fetch users: {e}")
            mentees, mentors = [], []
    
        if not mentees or not mentors:
            st.warning("No available mentees or mentors.")
        else:
            mentee_options = ["-- Select Mentee --"] + [m["email"] for m in mentees]
            mentor_options = ["-- Select Mentor --"] + [m["email"] for m in mentors]
    
            mentee_email = st.selectbox("Mentee Email", mentee_options, index=0, key="mentee_select")
            mentor_email = st.selectbox("Mentor Email", mentor_options, index=0, key="mentor_select")
    
            if st.button("Create Match"):
                if mentee_email == "-- Select Mentee --" or mentor_email == "-- Select Mentor --":
                    st.warning("⚠️ Please select both a valid mentee and mentor.")
                else:
                    st.session_state["selected_mentee_email"] = mentee_email
                    st.session_state["selected_mentor_email"] = mentor_email
                    st.success(f"✅ Mentee: {mentee_email}, Mentor: {mentor_email} are matched.")
                    time.sleep(1)
                    st.rerun()
    
            if "selected_mentee_email" in st.session_state and "selected_mentor_email" in st.session_state:
                if st.button("Create Match"):
                    mentee_email = st.session_state["selected_mentee_email"]
                    mentor_email = st.session_state["selected_mentor_email"]
    
                    if mentee_email == mentor_email:
                        st.warning("Mentee and Mentor cannot be the same.")
                    else:
                        mentee_id = next((m["userid"] for m in mentees if m["email"] == mentee_email), None)
                        mentor_id = next((m["userid"] for m in mentors if m["email"] == mentor_email), None)
    
                        existing = supabase.table("mentorshiprequest") \
                            .select("mentorshiprequestid") \
                            .eq("menteeid", mentee_id).eq("mentorid", mentor_id) \
                            .execute().data
    
                        if existing:
                            st.warning("⚠️ This mentorship request already exists.")
                        else:
                            availability = supabase.table("availability") \
                                .select("availabilityid") \
                                .eq("mentorid", mentor_id).execute().data
    
                            if not availability:
                                st.warning("⚠️ This mentor has no availability slots set.")
                            else:
                                supabase.table("mentorshiprequest").insert({
                                    "menteeid": mentee_id,
                                    "mentorid": mentor_id,
                                    "status": "ACCEPTED"
                                }).execute()
    
                                now = datetime.now(tz=WAT)
                                end = now + timedelta(minutes=30)
                                success, msg = create_session_if_available(supabase, mentor_id, mentee_id, now, end)
    
                                if success:
                                    st.success("✅ Match created and session booked!")
                                else:
                                    st.warning(msg)
                                st.rerun()

    # Sessions
    with tabs[3]:
        st.subheader("All Sessions")
        try:
            sessions = supabase.table("session").select("""
                *, mentor:users!session_mentorid_fkey(email),
                   mentee:users!session_menteeid_fkey(email)
            """).execute().data
        except Exception as e:
            st.error(f"❌ Could not fetch sessions: {e}")
            sessions = []

        if sessions:
            for s in sessions:
                start_time = s.get("date")
                status = session_status_label(start_time)

                st.markdown(f"""
                - 🧑‍🏫 Mentor: **{s['mentor']['email']}**  
                - 🧑 Mentee: **{s['mentee']['email']}**  
                - 📅 Start Time: {format_datetime_safe(s.get('date'))}  
                - 🕒 Status: {status}  
                - ⭐ Rating: {s.get('rating', 'Not rated')}  
                - 💬 Feedback: {s.get('feedback', 'No feedback')}  
                - 🔗 [Join Meet]({s.get('meet_link', '#')})
                """)
        else:
            st.info("No sessions found.")
            
    # --- Analytics Tab ---
    with tabs[4]:
        st.markdown(
            "<h2 style='text-align: center;'>📊 Platform Insights</h2>",
            unsafe_allow_html=True
        )
    
        try:
            users = supabase.table("users").select("userid, email, created_at, role, status").execute().data or []
            sessions = supabase.table("session").select("date, rating, mentorid, menteeid").execute().data or []
            requests = supabase.table("mentorshiprequest").select("status, createdat, menteeid").execute().data or []
        except Exception as e:
            st.error(f"❌ Failed to load analytics data: {e}")
            return
    
        df_users = pd.DataFrame(users)
        df_sessions = pd.DataFrame(sessions)
        df_requests = pd.DataFrame(requests)
    
        # --- Date Filters ---
        st.markdown("### 🗂️ Filter by Month and Year")
        date_pool = pd.concat([
            pd.to_datetime(df_users.get("created_at"), errors="coerce"),
            pd.to_datetime(df_sessions.get("date"), errors="coerce"),
            pd.to_datetime(df_requests.get("createdat"), errors="coerce")
        ]).dropna()
    
        filter_df = pd.DataFrame({"datetime": date_pool})
        filter_df["datetime"] = pd.to_datetime(filter_df["datetime"], errors="coerce")
        filter_df = filter_df.dropna(subset=["datetime"])
        filter_df["Year"] = filter_df["datetime"].dt.year
        filter_df["Month"] = filter_df["datetime"].dt.strftime("%B")
    
        years = sorted(filter_df["Year"].dropna().unique().tolist())
        months = filter_df["Month"].dropna().unique().tolist()
    
        years_with_all = ["All"] + years
        months_with_all = ["All"] + months
    
        selected_year = st.selectbox("📅 Select Year", years_with_all, index=len(years_with_all) - 1)
        selected_month = st.selectbox("🗓️ Select Month", months_with_all)
    
        # --- Apply Filters ---
        for df, date_col in [(df_users, "created_at"), (df_sessions, "date"), (df_requests, "createdat")]:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            df.dropna(subset=[date_col], inplace=True)
            df["Year"] = df[date_col].dt.year
            df["Month"] = df[date_col].dt.strftime("%B")
    
        if selected_year != "All":
            df_users = df_users[df_users["Year"] == selected_year]
            df_sessions = df_sessions[df_sessions["Year"] == selected_year]
            df_requests = df_requests[df_requests["Year"] == selected_year]
    
        if selected_month != "All":
            df_users = df_users[df_users["Month"] == selected_month]
            df_sessions = df_sessions[df_sessions["Month"] == selected_month]
            df_requests = df_requests[df_requests["Month"] == selected_month]
    
        # --- Mentor & Mentee Filters ---
        mentor_options = df_users[df_users["role"] == "Mentor"]["email"].dropna().unique().tolist()
        mentee_options = df_users[df_users["role"] == "Mentee"]["email"].dropna().unique().tolist()
    
        selected_mentor_email = st.selectbox("👨‍🏫 Filter by Mentor", ["All"] + mentor_options)
        selected_mentee_email = st.selectbox("🧑‍🎓 Filter by Mentee", ["All"] + mentee_options)
    
        mentor_lookup = df_users[df_users["role"] == "Mentor"][["userid", "email"]]
        mentee_lookup = df_users[df_users["role"] == "Mentee"]["userid"].to_frame().merge(df_users, on="userid")
    
        df_sessions_merged = df_sessions.copy()
        df_sessions_merged = df_sessions_merged.merge(mentor_lookup, left_on="mentorid", right_on="userid", how="left", suffixes=("", "_mentor"))
        df_sessions_merged = df_sessions_merged.merge(mentee_lookup[["userid", "email"]], left_on="menteeid", right_on="userid", how="left", suffixes=("", "_mentee"))
    
        if selected_mentor_email != "All":
            df_sessions_merged = df_sessions_merged[df_sessions_merged["email"] == selected_mentor_email]
    
        if selected_mentee_email != "All":
            df_sessions_merged = df_sessions_merged[df_sessions_merged["email_mentee"] == selected_mentee_email]
    
        # View filtered sessions
        st.markdown("### ⭐ Filtered Sessions View")
        st.dataframe(df_sessions_merged, use_container_width=True)
    
        # Note: Replace all references to df_sessions with df_sessions_merged from here onward
    
        # Example:
        # df_sessions = df_sessions_merged
    
        # Continue with metrics, charts, etc.
        # Your downstream logic and visualizations continue here as normal using the filtered data.

    
        # --- Metrics ---
        st.markdown("### 📌 Key Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("👥 Total Users", len(df_users))
        col2.metric("🧑‍🏫 Mentors", len(df_users[df_users.role == "Mentor"]))
        col3.metric("🧑 Mentees", len(df_users[df_users.role == "Mentee"]))
    
        col4, col5 = st.columns(2)
        col4.metric("📅 Total Sessions", len(df_sessions_merged))
        col5.metric("📩 Total Requests", len(df_requests))
    
        # --- Users Over Time ---
        st.markdown("### 📈 User Registrations Over Time")
        df_users["created_at"] = pd.to_datetime(df_users["created_at"], errors='coerce')
        df_users = df_users.dropna(subset=["created_at"])
        df_users["Month"] = df_users["created_at"].dt.to_period("M").astype(str)
        user_growth = df_users.groupby(["Month", "role"]).size().reset_index(name="Count")
        fig = px.bar(user_growth, x="Month", y="Count", color="role", barmode="group", title="User Growth by Role")
        st.plotly_chart(fig, use_container_width=True)
    
        # --- Sessions Trend ---
        st.markdown("### 📆 Sessions Trend")
        df_sessions_merged["Month"] = df_sessions_merged["date"].dt.to_period("M").astype(str)
        monthly_sessions = df_sessions_merged.groupby("Month").size().reset_index(name="Sessions")
        fig2 = px.line(monthly_sessions, x="Month", y="Sessions", markers=True, title="Monthly Sessions")
        st.plotly_chart(fig2, use_container_width=True)
    
        # --- Ratings Summary ---
        st.markdown("### ⭐ Session Ratings Distribution")
        df_ratings = df_sessions.dropna(subset=["rating"])
        fig3 = px.histogram(df_ratings, x="rating", nbins=5, title="Ratings Given by Mentees")
        st.plotly_chart(fig3, use_container_width=True)
    
        # --- Requests Status ---
        st.markdown("### 📩 Request Status Breakdown")
        request_counts = df_requests["status"].value_counts().reset_index()
        request_counts.columns = ["Status", "Count"]
        fig4 = px.pie(request_counts, names="Status", values="Count", title="Request Status Distribution")
        st.plotly_chart(fig4, use_container_width=True)
    
        # --- Top Requesting Mentees ---
        st.markdown("### 📬 Top Requesting Mentees")
        try:
            requests = supabase.table("mentorshiprequest") \
                .select("menteeid, status, users:users!mentorshiprequest_menteeid_fkey(email)") \
                .execute().data or []
            df_requests = pd.DataFrame(requests)
            if not df_requests.empty and "menteeid" in df_requests.columns:
                requests_per_mentee = df_requests.groupby("menteeid").size().reset_index(name="RequestCount")
                df_requests["email"] = df_requests["users"].apply(lambda u: u.get("email", "Unknown") if isinstance(u, dict) else "Unknown")
                df_emails = df_requests[["menteeid", "email"]].drop_duplicates()
                top_mentees = requests_per_mentee.merge(df_emails, on="menteeid", how="left") \
                    .sort_values(by="RequestCount", ascending=False).head(5)
                st.dataframe(top_mentees[["email", "RequestCount"]], use_container_width=True)
            else:
                st.info("No mentorship requests found or 'menteeid' is missing.")
        except Exception as e:
            st.error(f"Error loading mentorship request stats: {e}")
    
        # --- Mentee Engagement ---
        st.markdown("### 🧑 Mentee Engagement")
        rated_sessions = df_sessions["rating"].notna().sum()
        feedback_rate = (rated_sessions / len(df_sessions) * 100) if len(df_sessions) > 0 else 0
        if not df_users.empty and not df_requests.empty and not df_sessions.empty:
            mentees = df_users[df_users["role"] == "Mentee"]
            mentee_count = len(mentees)
            requests_per_mentee = df_requests.groupby("menteeid").size().reset_index(name="RequestCount")
            avg_requests = requests_per_mentee["RequestCount"].mean() if not requests_per_mentee.empty else 0
            col1, col2, col3 = st.columns(3)
            col1.metric("📩 Avg. Requests per Mentee", f"{avg_requests:.2f}")
            mentees_with_sessions = df_sessions["menteeid"].nunique()
            session_percentage = (mentees_with_sessions / mentee_count * 100) if mentee_count > 0 else 0
            col2.metric("📅 Mentees with Sessions", f"{session_percentage:.1f}%")
            col3.metric("⭐ Feedback Submission Rate", f"{feedback_rate:.1f}%")
    
        # --- Mentor Performance ---
        st.markdown("### 🧑‍🏫 Mentor Performance")
        mentors = df_users[df_users["role"] == "Mentor"]
        availability = supabase.table("availability").select("mentorid").execute().data or []
        df_availability = pd.DataFrame(availability)
        slots_per_mentor = df_availability.groupby("mentorid").size().reset_index(name="SlotCount")
        avg_slots = slots_per_mentor["SlotCount"].mean() if not slots_per_mentor.empty else 0
        sessions_per_mentor = df_sessions.groupby("mentorid").size().reset_index(name="SessionCount")
        avg_sessions = sessions_per_mentor["SessionCount"].mean() if not sessions_per_mentor.empty else 0
        ratings_per_mentor = df_sessions.groupby("mentorid")["rating"].mean().reset_index(name="AvgRating")
        avg_rating = ratings_per_mentor["AvgRating"].mean() if not ratings_per_mentor.empty else 0
        col1, col2, col3 = st.columns(3)
        col1.metric("🕒 Avg. Availability Slots", f"{avg_slots:.2f}")
        col2.metric("📅 Avg. Sessions per Mentor", f"{avg_sessions:.2f}")
        col3.metric("⭐ Avg. Rating per Mentor", f"{avg_rating:.1f}")
    
        # --- Admin Actions ---
        st.markdown("### 👑 Admin Actions")
        admin_registrations = len(df_users)
        promotions = supabase.table("users").select("userid").eq("role", "Mentor").execute().data or []
        promotion_count = len(promotions)
        admin_matches = df_requests[df_requests["status"] == "ACCEPTED"].shape[0]
        col1, col2, col3 = st.columns(3)
        col1.metric("👥 Admin-Registered Users", admin_registrations)
        col2.metric("🚀 Mentees Promoted", promotion_count)
        col3.metric("🔁 Admin-Created Matches", admin_matches)
    
        # --- Skill-Based Insights ---
        st.markdown("### 🎯 Popular Skills")
        try:
            profiles = supabase.table("profile").select("skills, userid").execute().data or []
            user_roles = supabase.table("users").select("userid, role").execute().data or []
            df_profiles = pd.DataFrame(profiles).merge(pd.DataFrame(user_roles), on="userid")
        except Exception as e:
            st.error(f"❌ Failed to load profile data: {e}")
            df_profiles = pd.DataFrame()
        if not df_profiles.empty:
            all_skills = []
            for _, row in df_profiles.iterrows():
                skills = row["skills"]
                if skills:
                    all_skills.extend([skill.strip().lower() for skill in skills.split(",")])
            skill_counts = pd.Series(all_skills).value_counts().reset_index().head(5)
            skill_counts.columns = ["Skill", "Count"]
            col1, col2 = st.columns(2)
            col1.metric("🎯 Unique Skills", len(set(all_skills)))
            col2.metric("📊 Top Skill", skill_counts.iloc[0]["Skill"] if not skill_counts.empty else "N/A")
            fig_skills = px.bar(skill_counts, x="Skill", y="Count", title="Top 5 In-Demand Skills")
            st.plotly_chart(fig_skills, use_container_width=True)
    
        # --- Session Completion and Feedback ---
        st.markdown("### 📅 Session Completion and Feedback")
        now = datetime.now(WAT).replace(tzinfo=None)
        completed_sessions = df_sessions_merged[df_sessions_merged["date"] < now]
        completion_rate = (len(completed_sessions) / len(df_sessions_merged) * 100) if len(df_sessions_merged) > 0 else 0
        col1, col2 = st.columns(2)
        col1.metric("📅 Completed Sessions", len(completed_sessions))
        col2.metric("⭐ Feedback Rate", f"{feedback_rate:.1f}%")
    
        # --- Mentorship Success Rate ---
        st.markdown("### 🔁 Mentorship Success Rate")
        acceptance_rate = (df_requests["status"] == "ACCEPTED").mean() * 100
        st.metric("✅ Acceptance Rate", f"{acceptance_rate:.1f}%")
        try:
            requests_with_time = supabase.table("mentorshiprequest").select("status, createdat").execute().data or []
            df_requests_time = pd.DataFrame(requests_with_time)
            if not df_requests_time.empty:
                df_requests_time["createdat"] = pd.to_datetime(df_requests_time["createdat"], errors="coerce")
                df_requests_time = df_requests_time.dropna(subset=["createdat"])
                df_requests_time["Month"] = df_requests_time["createdat"].dt.to_period("M").astype(str)
                request_trend = df_requests_time.groupby(["Month", "status"]).size().reset_index(name="Count")
                fig = px.bar(request_trend, x="Month", y="Count", color="status", barmode="group", title="📈 Monthly Mentorship Request Status Trends")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No mentorship request data available for trend analysis.")
        except Exception as e:
            st.error(f"Error fetching mentorship request trends: {e}")
