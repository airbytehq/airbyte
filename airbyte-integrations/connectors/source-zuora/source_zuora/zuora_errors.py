#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys
from typing import Any

import requests
from airbyte_cdk.logger import AirbyteLogger


class Error(Exception):
    """Base Error class for other exceptions"""

    # Define the instance of the Native Airbyte Logger
    logger = AirbyteLogger()


class QueryWindowError(Error):
    def __init__(self, value: Any):
        self.message = f"`Query Window` is set to '{value}', please make sure you use float or integer, not string."
        super().__init__(self.logger.info(self.message))
        # Exit with non-zero status
        sys.exit(1)


class ZOQLQueryError(Error):
    """Base class for  ZOQL EXPORT query errors"""

    def __init__(self, response: requests.Response = None):
        if response:
            self.response = response.json()
            self.error_msg = self.response["data"]["errorMessage"]
            self.query = self.response["data"]["query"]
            super().__init__(self.logger.error(f"{self.error_msg}, QUERY: {self.query}"))
        # Exit with non-zero status
        sys.exit(1)


class ZOQLQueryFailed(ZOQLQueryError):
    """Failed to execute query on the server side"""


class ZOQLQueryFieldCannotResolveCursor(Error):
    """
    Failed to execute query on the server side because of the certain field could not be resolved
    This exception is used to switch the default cursor_field inside the query.
    """

    def __init__(self, message: str = "Cursor 'UpdatedDate' is not available. Switching cursor to 'CreatedDate'"):
        super().__init__(self.logger.info(message))


class ZOQLQueryFieldCannotResolveAltCursor(Error):
    """
    Failed to execute query on the server side because of the certain field could not be resolved
    This exception is used to switch the default cursor_field inside the query.
    """

    def __init__(self, message: str = "Cursor 'CreatedDate' is not available. Fetching whole object"):
        super().__init__(self.logger.info(message))


class ZOQLQueryCannotProcessObject(Error):
    """
    The error raises when the user doesn't have the right permissions to read certain Zuora Object,
    or the object cannot be read due to technical reasons, we receive something like: 'failed to process object' msg,
    We trying to skip reading this stream, return [] as output and continue to read other streams
    """

    def __init__(
        self,
        message: str = "The stream cannot be processed, check Zuora Object's Permissions / Subscription Plan / API User Permissions, etc. This warning is not critical, and could be ignored.",
    ):
        super().__init__(self.logger.warn(message))
        pass
