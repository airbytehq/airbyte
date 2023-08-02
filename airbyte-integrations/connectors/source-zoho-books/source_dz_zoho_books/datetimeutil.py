from datetime import datetime
from dateutil import parser, tz

def convert_to_utc(start_date):
    dt = parser.parse(start_date)
    dt_utc = dt.astimezone(tz.tzutc())
    utc_str = dt_utc.strftime('%Y-%m-%dT%H:%M:%SZ')

    return datetime.strptime(utc_str, '%Y-%m-%dT%H:%M:%SZ')