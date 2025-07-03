from datetime import datetime, timedelta, timezone
from database import supabase
import pytz

# Define WAT timezone for any local conversions if needed
WAT = pytz.timezone("Africa/Lagos")

def cancel_stale_requests():
    """
    Cancels mentorship requests older than 48 hours that are still PENDING.
    Assumes 'created_at' is stored in UTC ISO format.
    """
    try:
        # Get current UTC time and subtract 48 hours for cutoff
        cutoff_time_utc = datetime.now(timezone.utc) - timedelta(hours=48)

        # Query all PENDING requests older than cutoff time
        response = supabase.table("mentorshiprequest") \
            .select("id, created_at") \
            .eq("status", "PENDING") \
            .lt("created_at", cutoff_time_utc.isoformat()) \
            .execute()

        stale_requests = response.data or []

        if not stale_requests:
            print("ℹ️ No stale requests found.")
            return

        for req in stale_requests:
            # Update status to CANCELLED for each stale request
            supabase.table("mentorshiprequest") \
                .update({"status": "CANCELLED"}) \
                .eq("id", req["id"]) \
                .execute()
            print(f"✅ Cancelled request ID: {req['id']}")

        print(f"🔁 Total cancelled stale requests: {len(stale_requests)}")

    except Exception as e:
        print(f"❌ Error while cancelling stale requests: {e}")
