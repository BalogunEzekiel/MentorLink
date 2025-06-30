from datetime import datetime, timedelta
from database import supabase
from postgrest.exceptions import APIError

def create_session(mentor_id: str, mentee_id: str, mentorshiprequest_id: str = None, days_from_now: int = 1):
    """
    Creates a session between a mentor and mentee.

    Args:
        mentor_id (str): ID of the mentor.
        mentee_id (str): ID of the mentee.
        mentorshiprequest_id (str, optional): ID of the related mentorship request.
        days_from_now (int): Number of days from now to schedule the session.

    Returns:
        dict: A dictionary with success status and session info or error message.
    """

    try:
        # Check if session already exists for the same request
        if mentorshiprequest_id:
            existing_session = supabase.table("session") \
                .select("sessionid") \
                .eq("mentorshiprequestid", mentorshiprequest_id) \
                .execute()

            if existing_session.data:
                return {
                    "success": False,
                    "message": "Session already exists for this mentorship request."
                }

        # Generate session date
        session_date = datetime.now() + timedelta(days=days_from_now)

        # Create session
        session_data = {
            "mentorid": mentor_id,
            "menteeid": mentee_id,
            "date": session_date.isoformat()
        }

        if mentorshiprequest_id:
            session_data["mentorshiprequestid"] = mentorshiprequest_id

        inserted = supabase.table("session").insert(session_data).execute()

        return {
            "success": True,
            "message": "Session created successfully.",
            "session": inserted.data[0] if inserted.data else session_data
        }

    except APIError as e:
        return {
            "success": False,
            "message": f"API error: {e}"
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error: {e}"
        }
