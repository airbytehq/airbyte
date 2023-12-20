import datetime
import os
from typing import Optional
from airbyte_lib.version import get_version
import requests


TRACKING_KEY = "jxT1qP9WEKwR3vtKMwP9qKhfQEGFtIM1"

def track(source: str, state: str, number_of_records: Optional[int] = None):
    # If DO_NOT_TRACK is set, we don't send any telemetry
    if os.environ.get("DO_NOT_TRACK"):
        return

    current_time = datetime.datetime.utcnow().isoformat()
    payload = {
        "anonymousId": "airbyte-lib-user",
        "event": "sync",
        "properties": {
            "version": get_version(),
            "source": source,
            "state": state,
            # explicitly set to 0.0.0.0 to avoid leaking IP addresses
            "ip": "0.0.0.0",
        },
        "timestamp": current_time
    }
    if number_of_records is not None:
        payload["properties"]["number_of_records"] = number_of_records

    # Do not handle the response, we don't want to block the execution
    requests.post("https://api.segment.io/v1/track", auth=(TRACKING_KEY, ""), json=payload)

