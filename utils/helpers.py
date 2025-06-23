# Shared functions for filters, formatting, etc.
def format_datetime(dt_string):
    from datetime import datetime
    return datetime.strptime(dt_string, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d %b %Y %I:%M %p")
