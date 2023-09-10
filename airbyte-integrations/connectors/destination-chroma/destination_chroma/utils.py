#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re
from ipaddress import ip_address



def validate_collection_name(stream_name: str):
    if is_valid_collection_name(stream_name):
        return stream_name
    # Remove characters that are not lowercase letters, digits, dots, dashes, or underscores
    valid_chars = re.sub(r'[^A-Za-z0-9._-]', '', stream_name)
    # Ensure the resulting name is within length constraints
    truncated_name = valid_chars[:63]
    # If the resulting name is too short, add some characters to meet the minimum length
    while len(truncated_name) < 3:
        truncated_name += 'x'
    # Ensure the resulting name starts and ends with a lowercase letter or digit
    if not truncated_name[0].isalnum():
        truncated_name = 'x' + truncated_name
    if not truncated_name[-1].isalnum():
        truncated_name = truncated_name + 'x'
    if truncated_name[0].isalpha() and truncated_name[0].isupper():
        truncated_name = truncated_name[0].lower() + truncated_name[1:]
    if truncated_name[-1].isalpha() and truncated_name[-1].isupper():
        truncated_name = truncated_name[:-1] + truncated_name[-1].lower()
    # remove consecutive dots
    truncated_name = truncated_name.replace('..', '')
    # remove all dots to invalidate ip address 
    try:
        ip_address(truncated_name)
        truncated_name = truncated_name.replace('.', '')
    except:
        pass
    return truncated_name

def is_valid_collection_name(stream_name: str):
    # Check length constraint
    if len(stream_name) < 3 or len(stream_name) > 63:
        return False
    # Check lowercase letter or digit at start and end
    if not (stream_name[0].islower() or stream_name[0].isdigit()) or not (stream_name[-1].islower() or stream_name[-1].isdigit()):
        return False
    # Check allowed characters
    if not re.match(r'^[a-z0-9._-]+$', stream_name):
        return False
    # Check consecutive dots
    if '..' in stream_name:
        return False
    # Check for valid IP address (a simple example)
    try:
        ip_address(stream_name)
        return False
    except:
        pass
    return True
