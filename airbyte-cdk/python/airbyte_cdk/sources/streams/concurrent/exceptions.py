#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


class ExceptionWithDisplayMessage(Exception):
    def __init__(self, display_message: str, **kwargs):
        super().__init__(**kwargs)
        self.display_message = display_message
