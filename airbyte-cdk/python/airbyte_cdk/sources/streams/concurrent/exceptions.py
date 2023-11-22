#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any


class ExceptionWithDisplayMessage(Exception):
    """
    Exception that can be used to display a custom message to the user.
    """

    def __init__(self, display_message: str, **kwargs: Any):
        super().__init__(**kwargs)
        self.display_message = display_message
