#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


class BambooHrError(Exception):
    message = ""

    def __init__(self):
        super().__init__(self.message)

class AvailableFieldsAccessDeniedError(BambooHrError):
    message = "You hasn't access to any report fields. Please check your access level."

