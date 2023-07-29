#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text
