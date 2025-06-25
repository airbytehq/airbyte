#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import os


def is_prod() -> bool:
    """Returns True if environment variable is prod, False otherwise."""
    prod = os.environ.get("PROD", "False").lower() in ("true", "1", "t")
    return prod


def is_dev() -> bool:
    """Return True if no environment variable is set, False otherwise."""
    return not is_prod()
