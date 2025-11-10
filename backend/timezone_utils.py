"""
Timezone utility functions for converting UTC to IST
"""
from datetime import datetime, timezone, timedelta
import pytz

# Define IST timezone
IST = pytz.timezone('Asia/Kolkata')

def utc_to_ist(utc_datetime):
    """Convert UTC datetime to IST"""
    if utc_datetime is None:
        return None
    
    # If the datetime is naive (no timezone info), assume it's UTC
    if utc_datetime.tzinfo is None:
        utc_datetime = utc_datetime.replace(tzinfo=pytz.UTC)
    
    # Convert to IST
    ist_datetime = utc_datetime.astimezone(IST)
    return ist_datetime

def get_ist_now():
    """Get current time in IST"""
    return datetime.now(IST)

def format_ist_datetime(utc_datetime, format_string='%m/%d/%Y, %I:%M:%S %p'):
    """Format UTC datetime as IST string"""
    if utc_datetime is None:
        return None
        
    ist_datetime = utc_to_ist(utc_datetime)
    return ist_datetime.strftime(format_string)

def get_ist_isoformat(utc_datetime):
    """Get IST datetime in ISO format"""
    if utc_datetime is None:
        return None
        
    ist_datetime = utc_to_ist(utc_datetime)
    return ist_datetime.isoformat()