#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module contains the exceptions used by the base_images module."""

from typing import Union

import dagger


class SanityCheckError(Exception):
    """Raised when a sanity check fails."""

    def __init__(self, error: Union[str, dagger.ExecError], *args: object) -> None:
        super().__init__(error, *args)
