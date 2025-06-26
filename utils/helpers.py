# Shared functions for filters, formatting, etc.
def format_datetime(dt_string):
    from datetime import datetime
    import pytz

    try:
        # Try format with T and Z (UTC)
        dt = datetime.strptime(dt_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        try:
            # Try format with space, assuming UTC
            dt = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            return "Invalid date"

    # Convert from UTC to local time (adjust as needed)
    utc = pytz.utc
    local_tz = pytz.timezone("Africa/Lagos")  # or use `pytz.timezone('Etc/UTC')` or `pytz.timezone('US/Eastern')`

    dt_utc = utc.localize(dt)
    dt_local = dt_utc.astimezone(local_tz)

    return dt_local.strftime("%d %b %Y %H:%M")
