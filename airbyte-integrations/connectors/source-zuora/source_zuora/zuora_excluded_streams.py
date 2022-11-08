#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import List

"""
This list holds the Zuora Object names (API object names) that could not be processed or
plays the service role for other objects and doesn't hold the actual data, while being called using API call.
Extend this list if needed.
"""

ZUORA_EXCLUDED_STREAMS: List = [
    "aggregatedataqueryslowdata",
]
