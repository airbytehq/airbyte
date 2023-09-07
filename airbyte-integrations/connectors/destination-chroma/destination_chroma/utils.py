#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re

def validate_collection_name(stream_name):
    if is_valid_collection_name(stream_name):
        return stream_name
    
    # Remove characters that are not lowercase letters, digits, dots, dashes, or underscores
    valid_chars = re.sub(r'[^a-z0-9._-]', '', stream_name)

    # Ensure the resulting name is within length constraints
    truncated_name = valid_chars[:63]

    # If the resulting name is too short, add some characters to meet the minimum length
    while len(truncated_name) < 3:
        truncated_name += 'x'
        
    # Ensure the resulting name starts and ends with a lowercase letter or digit
    if truncated_name[0].isdigit():
        truncated_name = 'a' + truncated_name[1:]
    if not truncated_name[-1].isalnum():
        truncated_name = truncated_name[:-1] + 'a'
    
    return truncated_name

def is_valid_collection_name(stream_name):
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
    if re.match(r'^(?:(?!\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?:(?:(?!\-|\.)[a-z0-9_\-\.])+[a-z0-9])?)$', stream_name):
        return False
    return True
