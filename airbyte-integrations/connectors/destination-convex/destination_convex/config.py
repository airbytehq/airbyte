#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import TypedDict


ConvexConfig = TypedDict(
    "ConvexConfig",
    {
        "deployment_url": str,
        "access_key": str,
    },
)
