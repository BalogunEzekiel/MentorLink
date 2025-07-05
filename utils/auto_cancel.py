# utils/auto_cancel.py

from datetime import datetime, timedelta
from dateutil import parser
from database import supabase
import pytz
import time
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define West Africa Time (WAT)
WAT = pytz.timezone("Africa/Lagos")

def retry_supabase_query(query_func, retries=3, delay=2):
    """Retries a Supabase query up to `retries` times with delay."""
    for attempt in range(retries):
        try:
            return query_func()
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise e

def cancel_expired_requests():
    """
    Automatically cancel mentorship requests that have been pending for more than 48 hours.
    Updates status to 'CANCELLED_AUTO'.
    """
    try:
        response = retry_supabase_query(lambda: supabase
            .table("mentorshiprequest")
            .select("mentorshiprequestid, createdat, status")
            .eq("status", "PENDING")
            .execute()
        )

        pending_requests = response.data or []
        now_wat = datetime.now(WAT)

        logger.info(f"Checking {len(pending_requests)} pending requests...")

        for req in pending_requests:
            try:
                created_at = parser.isoparse(req["createdat"])

                # Ensure datetime is timezone-aware in WAT
                if created_at.tzinfo is None:
                    created_at = WAT.localize(created_at)
                else:
                    created_at = created_at.astimezone(WAT)

                # Cancel if older than 48 hours
                if now_wat - created_at > timedelta(hours=48):
                    supabase.table("mentorshiprequest") \
                        .update({"status": "CANCELLED_AUTO"}) \
                        .eq("mentorshiprequestid", req["mentorshiprequestid"]) \
                        .execute()

                    logger.info(f"✅ Auto-cancelled request: {req['mentorshiprequestid']}")

            except Exception as inner_err:
                logger.warning(f"⚠️ Skipped request {req.get('mentorshiprequestid')} due to: {inner_err}")

    except Exception as outer_err:
        logger.error(f"❌ Failed to process expired mentorship requests: {outer_err}")
