#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream


def read_full_refresh(stream_instance: Stream):
    slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh)
    for _slice in slices:
        records = stream_instance.read_records(stream_slice=_slice, sync_mode=SyncMode.full_refresh)
        for record in records:
            yield record


# Precompile the regex pattern.
ISO_FORMAT_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})[ t](\d{2}:\d{2}:\d{2})$")


def to_iso_format(s: str) -> str:
    """
    Convert a date string to ISO format if it matches recognized patterns.

    Args:
    - s (str): Input string to be converted.

    Returns:
    - str: Converted string in ISO format or the original string if no recognized pattern is found.
    """
    # Use the precompiled regex pattern to match the date format.
    match = ISO_FORMAT_PATTERN.match(s)
    if match:
        return match.group(1) + "T" + match.group(2)

    return s


def fix_date_time(record):
    """
    Recursively process a data structure to fix date and time formats.

    Args:
    - record (dict or list): The input data structure, which can be a dictionary or a list.

    Returns:
    - None: The function modifies the input data structure in place.
    """
    # Define the list of fields that might contain date and time values.
    date_time_fields = {"last_seen", "created", "last_authenticated"}

    if isinstance(record, dict):
        for field, value in list(record.items()):  # Convert to list to avoid runtime errors during iteration.
            if field in date_time_fields and isinstance(value, str):
                record[field] = to_iso_format(value)
            elif isinstance(value, (dict, list)):
                fix_date_time(value)

    elif isinstance(record, list):
        for entry in record:
            fix_date_time(entry)
