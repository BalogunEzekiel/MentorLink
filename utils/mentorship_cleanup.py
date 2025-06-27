from datetime import datetime, timedelta
from database import supabase

def cancel_stale_requests():
    """Cancels mentorship requests older than 48 hours that are still PENDING."""
    cutoff_time = datetime.utcnow() - timedelta(hours=48)

    response = supabase.table("mentorshiprequest") \
        .select("id, created_at") \
        .eq("status", "PENDING") \
        .lt("created_at", cutoff_time.isoformat()) \
        .execute()

    stale_requests = response.data

    for req in stale_requests:
        supabase.table("mentorshiprequest") \
            .update({"status": "CANCELLED"}) \
            .eq("id", req["id"]) \
            .execute()
