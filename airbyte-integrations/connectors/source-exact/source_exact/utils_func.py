#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import os


def is_prod() -> bool:
    """Returns True if environment variable prod is set, False otherwise."""
    prod = os.environ.get("PROD", "False").lower() in ("true", "1", "t")
    return prod


def is_dev() -> bool:
    """Return True if environment variable dev is set, False otherwise."""
    dev = os.environ.get("DEV", "False").lower() in ("true", "1", "t")
    return dev
