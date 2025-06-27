# utils/mentorchat.py

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
- Monitor user activities
- Access system analytics
- Update platform configurations

How can I assist with your admin tasks?"""
        elif user_role == "Mentor":
            return """👨‍🏫 As a Mentor, you can:
- Set your availability on the calendar
- View and accept session requests
- Update your profile and mentoring goals
- Respond to mentee messages

Need help with any of these?"""
        else:  # Mentee
            return """🎯 As a Mentee, you can:
- Browse available mentors
- Request and schedule sessions
- Complete your profile and goals
- Track mentorship progress on your dashboard

Let me know what you want help with."""

    elif "availability" in user_input:
        if user_role == "Mentor":
            return "📆 To set your availability, go to your Mentor Dashboard > 'Manage Availability'."
        else:
            return "📅 Mentor availability can be checked from your Mentee Dashboard > 'Find Mentor'."

    elif "book" in user_input or "schedule" in user_input:
        return "🗓️ To schedule a session, use the 'Request Mentorship' button from your dashboard."

    elif "profile" in user_input:
        return "📝 You can complete or edit your profile from the menu or settings panel on your dashboard."

    elif "dashboard" in user_input:
        return f"📊 Navigate to the '{user_role.title()} Dashboard' from the sidebar to manage your activities."

    elif "messages" in user_input:
        return "💬 You can view and respond to mentorship messages from the top-right inbox icon."

    elif "who are you" in user_input or "what can you do" in user_input:
        return """🤖 I'm MentorChat, your assistant on MentorLink.
I help you understand and use the platform effectively, depending on your role (Admin, Mentor, or Mentee)."""

    elif any(bye in user_input for bye in farewells):
        return "👋 Goodbye! Wishing you a productive mentorship experience."

    elif any(word in user_input for word in gratitude):
        return "🙏 You're welcome! Always happy to help."

    else:
        return "🤔 I'm not sure I understood that. Try asking about mentors, booking, availability, dashboard, profile, or messages."
