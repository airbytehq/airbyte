#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module contains the exceptions used by the base_images module.
"""


class BaseImageVersionNotFoundError(ValueError):
    """Raised when the version of a base image is not found."""

    pass


class SanityCheckError(Exception):
    """Raised when a sanity check fails."""

    pass
