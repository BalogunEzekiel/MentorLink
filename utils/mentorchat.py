def mentorchat(user_input: str, user_role: str = "Mentee") -> str:
    user_input = user_input.strip().lower()

    greetings = ("hi", "hello", "hey", "good morning", "good afternoon", "good evening")
    farewells = ("bye", "goodbye", "see you", "take care", "later")
    gratitude = ("thank you", "thanks", "thx", "appreciate")
    help_requests = ("help", "support", "assist", "need help", "how do i")

    if any(greet in user_input for greet in greetings):
        return f"👋 Hello {user_role.title()}! I'm MentorChat. How can I support you on MentorLink today?"

    elif any(word in user_input for word in help_requests):
        if user_role == "Admin":
            return """🛠️ As an Admin, you can:
- Register new users (mentors & mentees)
- Monitor user activities and session logs
- View platform-wide analytics
- Update platform settings and configurations
- Manage roles and user status (active/inactive)
- Reset passwords and approve profile completions

Would you like help with user registration, analytics, or system settings?"""

        elif user_role == "Mentor":
            return """👨‍🏫 As a Mentor, you can:
- Complete your profile with name, skills, and mentoring goals
- Set and manage your availability calendar
- View mentorship requests from mentees
- Accept or reject session requests
- Chat with mentees and respond to inquiries
- Track upcoming sessions and mentorship impact

What would you like to do today—set availability, manage requests, or update your profile?"""

        else:  # Mentee
            return """🎯 As a Mentee, you can:
- Complete your profile with name, skills, and goals
- Browse available mentors by expertise or availability
- Send mentorship requests
- Track accepted or upcoming sessions
- Chat with mentors directly
- View your dashboard for progress and updates

Would you like help with booking, finding a mentor, or editing your profile?"""

    elif "availability" in user_input:
        if user_role == "Mentor":
            return "📆 To set your availability, go to your Mentor Dashboard and click on 'Manage Availability'. You can add specific time slots, set recurring availability, or block off dates."
        elif user_role == "Mentee":
            return "📅 You can check mentor availability from your Mentee Dashboard under 'Browse Mentor'. Filter by expertise or time to find a suitable mentor."
        else:
            return "🔍 Availability details are specific to mentor schedules. You can review them from the admin panel under 'Mentor Schedules'."

    elif "book" in user_input or "schedule" in user_input or "request" in user_input:
        if user_role == "Mentee":
            return "🗓️ To schedule a session, open your dashboard, go to 'Browse Mentor', select a mentor, and click 'Request Mentorship'. You'll receive a confirmation once the mentor responds."
        elif user_role == "Mentor":
            return "🗂️ You can respond to mentorship requests from your dashboard under 'Pending Requests'. Accept or decline, and confirm the session time with the mentee."
        else:
            return "📊 As Admin, you can oversee session bookings, review scheduling conflicts, and monitor activity logs in the analytics panel."

    elif "profile" in user_input:
        return "📝 You can complete or edit your profile by clicking on your name (top-right), then selecting 'Edit Profile'. Ensure your skills, goals, and contact details are up-to-date for better mentor-mentee matching."

    elif "dashboard" in user_input:
        return f"📊 To manage your activities, navigate to the '{user_role.title()} Dashboard' from the sidebar. Here, you can view sessions, messages, and analytics specific to your role."

    elif "messages" in user_input or "chat" in user_input:
        return "💬 Mentorship messages are accessible through the top-right inbox icon or your session overview. You can reply to mentees or mentors directly and review past conversations."

    elif "register" in user_input or "create user" in user_input:
        if user_role == "Admin":
            return "➕ To register users, use the 'Register User' form on your Admin Dashboard. Provide email, role (Mentor/Mentee), and status (active/inactive). Ensure all fields are validated before submission."
        else:
            return "🔐 Only Admins can register new users. Please contact support at [support@mentorlink.com](mailto:support@mentorlink.com) for account access or registration issues."

    elif "track progress" in user_input or "progress" in user_input:
        if user_role == "Mentee":
            return "📈 You can view your mentorship progress, completed sessions, and goal milestones from your dashboard under 'My Sessions'. Use the progress tracker to review feedback from mentors."
        elif user_role == "Mentor":
            return "📊 Mentors can track mentee engagements, session history, and feedback from the Mentor Dashboard under 'Mentorship Impact'. Export reports for detailed insights."
        else:
            return "📉 Admins can oversee all users’ progress, session completion rates, and platform engagement metrics in the analytics and activity monitoring section."

    elif "change password" in user_input:
        return "🔐 To change your password, go to 'Settings' in your profile dropdown menu. Enter your current password, then your new password, and confirm. Ensure it meets security requirements (8+ characters, mix of letters and numbers)."

    elif "support" in user_input or "contact" in user_input:
        return "📞 For technical support or questions, click 'Contact Us' in the sidebar or reach out via [chat with support](https://wa.me/2348062529172) or email [support@mentorlink.com](mailto:support@mentorlink.com)."

    elif "who are you" in user_input or "what can you do" in user_input:
        return """🤖 I'm MentorChat, your AI assistant on MentorLink.
I help you navigate the platform, understand your role, and perform tasks more easily—whether you're an Admin, Mentor, or Mentee. Ask me about profiles, scheduling, analytics, or anything MentorLink-related!"""

    elif any(bye in user_input for bye in farewells):
        return "👋 Goodbye! Wishing you a productive mentorship experience on MentorLink."

    elif any(word in user_input for word in gratitude):
        return "🙏 You're welcome! Let me know if there’s anything else I can assist you with."

    elif "mentor expertise" in user_input or "browse mentor" in user_input:
        if user_role == "Mentee":
            return "🔎 To find a mentor, go to 'Browse Mentor' on your dashboard. Filter by expertise (e.g., Python, Data Science, UX Design), availability, or ratings. Send a request to connect!"
        elif user_role == "Mentor":
            return "📚 As a mentor, you can showcase your expertise by updating your profile with skills and certifications. This helps mentees find you in their search."
        else:
            return "🔍 Admins can view mentor expertise and mentee preferences in the user management panel to optimize matching."

    elif "session feedback" in user_input or "review" in user_input:
        if user_role == "Mentee":
            return "⭐ After a session, you can provide feedback via the 'My Sessions' section. Rate your mentor and share comments to help improve future sessions."
        elif user_role == "Mentor":
            return "📝 You can submit session feedback or review mentee progress in the 'Mentorship Impact' section. Feedback helps track growth and improve mentoring."
        else:
            return "📊 Admins can review all session feedback in the analytics panel to ensure quality and address any concerns."

    elif "cancel session" in user_input or "reschedule" in user_input:
        if user_role == "Mentee":
            return "🗑️ To cancel or reschedule a session, go to 'My Sessions', select the session, and choose 'Cancel' or 'Reschedule'. Notify your mentor promptly."
        elif user_role == "Mentor":
            return "🗓️ You can cancel or reschedule sessions in the 'Upcoming Sessions' section. Notify mentees and update your availability accordingly."
        else:
            return "🔧 Admins can manage session cancellations or rescheduling requests via the session logs in the admin panel."

    elif "platform analytics" in user_input or "reports" in user_input:
        if user_role == "Admin":
            return "📈 Access platform analytics via the Admin Dashboard under 'Analytics'. View metrics like active users, session completion rates, and mentor-mentee engagement."
        else:
            return "🔍 Analytics are available to Admins only. Contact your admin or [support@mentorlink.com](mailto:support@mentorlink.com) for insights."

    elif "notifications" in user_input:
        return "🔔 Manage notifications in 'Settings' from your profile dropdown. Customize alerts for new messages, session requests, or platform updates."

    elif "mentor matching" in user_input or "match" in user_input:
        if user_role == "Mentee":
            return "🤝 Mentor matching is based on your goals and mentor expertise. Update your profile with clear objectives and use 'Browse Mentor' to explore matches."
        elif user_role == "Mentor":
            return "🤝 Ensure your profile reflects your expertise and availability to improve mentor-mentee matching. Check pending requests in your dashboard."
        else:
            return "🔧 Admins can oversee mentor-mentee matching algorithms and manually adjust matches in the user management panel."

    elif "faq" in user_input or "frequently asked questions" in user_input:
        return """❓ **MentorLink FAQ**:
- **How do I find a mentor?** Go to 'Browse Mentor' on your dashboard, filter by expertise or availability, and send a request.
- **How do I set up my profile?** Click your name (top-right), select 'Edit Profile', and add skills, goals, and contact info.
- **Can I cancel a session?** Yes, in 'My Sessions', select the session and choose 'Cancel' or 'Reschedule'.
- **How do I contact support?** Use the 'Contact Us' link or email [support@mentorlink.com](mailto:support@mentorlink.com).
- **Where do I see my progress?** Check 'My Sessions' (Mentees) or 'Mentorship Impact' (Mentors) on your dashboard.
- **How do Admins monitor activity?** Use the Admin Dashboard's analytics panel for user activity and session logs.
Want more details on any of these?"""

    else:
        return """🤔 I’m not sure I understood that. Try asking about:
- Setting availability
- Booking or canceling a session
- Completing your profile
- Viewing your dashboard
- Registering users
- Tracking progress
- Changing your password
- Mentor matching or expertise
- Session feedback or platform analytics
- Notifications or FAQs
"""
