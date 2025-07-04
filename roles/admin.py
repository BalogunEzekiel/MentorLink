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
            mentee_email = st.selectbox("Select Mentee", [m["email"] for m in mentees])
            mentor_email = st.selectbox("Select Mentor", [m["email"] for m in mentors])

            if st.button("Create Match"):
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
                        st.warning("This mentorship request already exists.")
                    else:
                        availability = supabase.table("availability") \
                            .select("availabilityid") \
                            .eq("mentorid", mentor_id).execute().data

                        if not availability:
                            st.warning("⚠️ This mentor has no availability slots set.")

                        supabase.table("mentorshiprequest").insert({
                            "menteeid": mentee_id,
                            "mentorid": mentor_id,
                            "status": "ACCEPTED"
                        }).execute()

                        now = datetime.now(tz=WAT)
                        end = now + pd.Timedelta(minutes=30)
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
                st.markdown(f"""
                - 🧑‍🏫 Mentor: **{s['mentor']['email']}**  
                - 🧑 Mentee: **{s['mentee']['email']}**  
                - 📅 Date: {format_datetime_safe(s.get('date'))}  
                - ⭐ Rating: {s.get('rating', 'Not rated')}  
                - 💬 Feedback: {s.get('feedback', 'No feedback')}  
                - 🔗 [Join Meet]({s.get('meet_link', '#')})
                """)
        else:
            st.info("No sessions found.")

    # --- Analytics Tab ---
    with tabs[4]:
        st.subheader("📊 Platform Insights")

        try:
            users = supabase.table("users").select("userid, email, created_at, role, status").execute().data or []
            sessions = supabase.table("session").select("date, rating, mentorid, menteeid").execute().data or []
            requests = supabase.table("mentorshiprequest").select("status").execute().data or []
        except Exception as e:
            st.error(f"❌ Failed to load analytics data: {e}")
            return

        df_users = pd.DataFrame(users)
        df_sessions = pd.DataFrame(sessions)
        df_requests = pd.DataFrame(requests)

        # --- Metrics ---
        st.markdown("### 📌 Key Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("👥 Total Users", len(df_users))
        col2.metric("🧑‍🏫 Mentors", len(df_users[df_users.role == "Mentor"]))
        col3.metric("🧑 Mentees", len(df_users[df_users.role == "Mentee"]))

        col4, col5 = st.columns(2)
        col4.metric("📅 Total Sessions", len(df_sessions))
        col5.metric("📩 Total Requests", len(df_requests))

        # --- Users Over Time ---
        st.markdown("### 📈 User Registrations Over Time")
        if "created_at" in df_users:
            df_users["created_at"] = pd.to_datetime(df_users["created_at"], errors='coerce')
            df_users = df_users.dropna(subset=["created_at"])
            df_users["Month"] = df_users["created_at"].dt.to_period("M").astype(str)
            user_growth = df_users.groupby(["Month", "role"]).size().reset_index(name="Count")
            fig = px.bar(user_growth, x="Month", y="Count", color="role", barmode="group", title="User Growth by Role")
            st.plotly_chart(fig, use_container_width=True)

        # --- Sessions Trend ---
        st.markdown("### 📆 Sessions Trend")
        if not df_sessions.empty:
            df_sessions["date"] = pd.to_datetime(df_sessions["date"], errors='coerce')
            df_sessions = df_sessions.dropna(subset=["date"])
            df_sessions["Month"] = df_sessions["date"].dt.to_period("M").astype(str)
            monthly_sessions = df_sessions.groupby("Month").size().reset_index(name="Sessions")
            fig2 = px.line(monthly_sessions, x="Month", y="Sessions", markers=True, title="Monthly Sessions")
            st.plotly_chart(fig2, use_container_width=True)

        # --- Ratings Summary ---
        st.markdown("### ⭐ Session Ratings Distribution")
        if "rating" in df_sessions:
            df_ratings = df_sessions.dropna(subset=["rating"])
            fig3 = px.histogram(df_ratings, x="rating", nbins=5, title="Ratings Given by Mentees")
            st.plotly_chart(fig3, use_container_width=True)

        # --- Requests Status ---
        st.markdown("### 📩 Request Status Breakdown")
        if not df_requests.empty:
            request_counts = df_requests["status"].value_counts().reset_index()
            request_counts.columns = ["Status", "Count"]
            fig4 = px.pie(request_counts, names="Status", values="Count", title="Request Status Distribution")
            st.plotly_chart(fig4, use_container_width=True)

        # --- Top Requesting Mentees ---
        st.markdown("### 📬 Top Requesting Mentees")
        
        # Get mentorship requests with mentee email
        try:
            requests = supabase.table("mentorshiprequest").select("menteeid, status, users:users!mentorshiprequest_menteeid_fkey(email)").execute().data or []
            requests = supabase.table("mentorshiprequest").select("mentorshiprequestid, menteeid, status, created_at").execute().data or []
            mentees = supabase.table("users").select("userid, email").eq("role", "Mentee").execute().data or []
            df_mentees = pd.DataFrame(mentees)

            df_requests = pd.DataFrame(requests)
        
            if not df_requests.empty and "menteeid" in df_requests.columns:
                # Group by mentee and count
                requests_per_mentee = df_requests.groupby("menteeid").size().reset_index(name="RequestCount")
        
                # Merge mentee emails (if available)
                if "users" in df_requests.columns:
                    df_emails = df_requests[["menteeid", "users"]].drop_duplicates()
                    df_emails["email"] = df_emails["users"].apply(lambda u: u.get("email", "Unknown"))
                    requests_per_mentee = requests_per_mentee.merge(df_emails, on="menteeid", how="left")

                # Sort and display top mentees
                top_mentees = requests_per_mentee.sort_values(by="RequestCount", ascending=False).head(5)
                st.dataframe(top_mentees[["email", "RequestCount"]], use_container_width=True)
            else:
                st.info("No mentorship requests found or 'menteeid' is missing.")
        except Exception as e:
            st.error(f"Error loading mentorship request stats: {e}")

        # --- Mentee Engagement ---
        st.markdown("### 🧑 Mentee Engagement")
        if not df_users.empty and not df_requests.empty and not df_sessions.empty:
            mentees = df_users[df_users["role"] == "Mentee"]
            mentee_count = len(mentees)
            
            # Requests per mentee
            requests_per_mentee = df_requests.groupby("menteeid").size().reset_index(name="RequestCount")
            avg_requests = requests_per_mentee["RequestCount"].mean() if not requests_per_mentee.empty else 0
            col1, col2, col3 = st.columns(3)
            col1.metric("📩 Avg. Requests per Mentee", f"{avg_requests:.2f}")
            
            # Mentees with sessions
            mentees_with_sessions = df_sessions["menteeid"].nunique()
            session_percentage = (mentees_with_sessions / mentee_count * 100) if mentee_count > 0 else 0
            col2.metric("📅 Mentees with Sessions", f"{session_percentage:.1f}%")
            
            # Feedback rate
            rated_sessions = df_sessions["rating"].notna().sum()
            feedback_rate = (rated_sessions / len(df_sessions) * 100) if len(df_sessions) > 0 else 0
            col3.metric("⭐ Feedback Submission Rate", f"{feedback_rate:.1f}%")
            
            # Visualization: Distribution of requests per mentee
            request_dist = requests_per_mentee["RequestCount"].value_counts().reset_index()
            request_dist.columns = ["Requests", "Mentees"]
            request_dist = request_dist.sort_values("Requests")

        # --- Mentor Performance ---
        st.markdown("### 🧑‍🏫 Mentor Performance")
        if not df_users.empty and not df_sessions.empty:
            mentors = df_users[df_users["role"] == "Mentor"]
            mentor_count = len(mentors)
            
            # Availability slots
            availability = supabase.table("availability").select("mentorid").execute().data or []
            df_availability = pd.DataFrame(availability)
            slots_per_mentor = df_availability.groupby("mentorid").size().reset_index(name="SlotCount")
            avg_slots = slots_per_mentor["SlotCount"].mean() if not slots_per_mentor.empty else 0
            
            # Sessions per mentor
            sessions_per_mentor = df_sessions.groupby("mentorid").size().reset_index(name="SessionCount")
            avg_sessions = sessions_per_mentor["SessionCount"].mean() if not sessions_per_mentor.empty else 0
            
            # Average rating per mentor
            ratings_per_mentor = df_sessions.groupby("mentorid")["rating"].mean().reset_index(name="AvgRating")
            avg_rating = ratings_per_mentor["AvgRating"].mean() if not ratings_per_mentor.empty else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("🕒 Avg. Availability Slots", f"{avg_slots:.2f}")
            col2.metric("📅 Avg. Sessions per Mentor", f"{avg_sessions:.2f}")
            col3.metric("⭐ Avg. Rating per Mentor", f"{avg_rating:.1f}")
            
            # Visualization: Top mentors by session count
            top_mentors = sessions_per_mentor.merge(df_users[["userid", "email"]], left_on="mentorid", right_on="userid")
            top_mentors = top_mentors.sort_values("SessionCount", ascending=False).head(5)

        # --- Admin Actions ---
        st.markdown("### 👑 Admin Actions")
        if not df_users.empty and not df_requests.empty:
            # Admin-registered users (all users, assuming admin-driven registration)
            admin_registrations = len(df_users)
            
            # Promotions (mentees who became mentors)
            promotions = supabase.table("users").select("userid").eq("role", "Mentor").execute().data or []
            promotion_count = len(promotions)  # Simplification; ideally, track role changes in a log table
            
            # Admin-created matches
            admin_matches = df_requests[df_requests["status"] == "ACCEPTED"].shape[0]
            
            col1, col2, col3 = st.columns(3)
            col1.metric("👥 Admin-Registered Users", admin_registrations)
            col2.metric("🚀 Mentees Promoted", promotion_count)
            col3.metric("🔁 Admin-Created Matches", admin_matches)
            
            # Visualization: Admin actions over time (registrations)
            admin_growth = df_users.groupby("Month").size().reset_index(name="Registrations")

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
            
            # Metrics
            col1, col2 = st.columns(2)
            col1.metric("🎯 Unique Skills", len(set(all_skills)))
            col2.metric("📊 Top Skill", skill_counts.iloc[0]["Skill"] if not skill_counts.empty else "N/A")
            
            # Visualization: Top 5 skills

        # --- Session Completion and Feedback ---
        st.markdown("### 📅 Session Completion and Feedback")
        if not df_sessions.empty:
            now = datetime.now(WAT)
            df_sessions["date"] = pd.to_datetime(df_sessions["date"], errors="coerce")
            completed_sessions = df_sessions[df_sessions["date"] < now]
            completion_rate = (len(completed_sessions) / len(df_sessions) * 100) if len(df_sessions) > 0 else 0
            
            col1, col2 = st.columns(2)
            col1.metric("📅 Completed Sessions", len(completed_sessions))
            col2.metric("⭐ Feedback Rate", f"{feedback_rate:.1f}%")  # From Mentee Engagement
            
            # Visualization: Completion vs. Feedback
            feedback_data = [
                {"Category": "Completed Sessions", "Count": len(completed_sessions)},
                {"Category": "Rated Sessions", "Count": rated_sessions}
            ]
            df_feedback = pd.DataFrame(feedback_data)

        # --- Mentorship Success Rate ---
        st.markdown("### 🔁 Mentorship Success Rate")
        
        if not df_requests.empty:
            # Acceptance rate
            acceptance_rate = (df_requests["status"] == "ACCEPTED").mean() * 100
            st.metric("✅ Acceptance Rate", f"{acceptance_rate:.1f}%")
        
            # Time-based trends
            try:
                requests_with_time = supabase.table("mentorshiprequest").select("status, created_at").execute().data or []
                df_requests_time = pd.DataFrame(requests_with_time)
        
                if not df_requests_time.empty:
                    df_requests_time["created_at"] = pd.to_datetime(df_requests_time["created_at"], errors="coerce")
                    df_requests_time["Month"] = df_requests_time["created_at"].dt.to_period("M").astype(str)
        
                    # Group by month and status
                    request_trend = df_requests_time.groupby(["Month", "status"]).size().reset_index(name="Count")
        
                    # Plotting
                    fig = px.bar(
                        request_trend,
                        x="Month",
                        y="Count",
                        color="status",
                        barmode="group",
                        title="📈 Monthly Mentorship Request Status Trends"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No mentorship request data available for trend analysis.")
            except Exception as e:
                st.error(f"Error fetching mentorship request trends: {e}")
        else:
            st.info("No mentorship requests available for analysis.")
