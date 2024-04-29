#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re
from ipaddress import ip_address


def is_valid_collection_name(stream_name: str):
    # Check length constraint
    if len(stream_name) < 3 or len(stream_name) > 63:
        return "The length of the collection name must be between 3 and 63 characters"
    # Check lowercase letter or digit at start and end
    if not (stream_name[0].islower() or stream_name[0].isdigit()) or not (stream_name[-1].islower() or stream_name[-1].isdigit()):
        return "The collection name must start and end with a lowercase letter or a digit"
    # Check allowed characters
    if not re.match("^[a-z0-9][a-zA-Z0-9._-]*[a-z0-9]$", stream_name):
        return "The collection name can only contain lower case alphanumerics, dots, dashes, and underscores"
    # Check consecutive dots
    if ".." in stream_name:
        return "The collection name must not contain two consecutive dots"
    # Check for valid IP address
    try:
        ip_address(stream_name)
        return "The collection name must not be a valid IP address."
    except ValueError:
        if re.match("^[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}$", stream_name):
            return "The collection name must not be a valid IP address."
        return
