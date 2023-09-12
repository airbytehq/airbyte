#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module contains the exceptions used by the base_images module.
"""


class BaseImageVersionError(ValueError):
    """Raised when the version is not in the expected format."""

    pass


class SanityCheckError(Exception):
    """Raised when a sanity check fails."""

    pass


class PlatformAvailabilityError(ValueError):
    """Raised when an image does not support the passed."""

    pass
