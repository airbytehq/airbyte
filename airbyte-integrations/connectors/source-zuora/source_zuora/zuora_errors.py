#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


import sys

import requests
from airbyte_cdk import AirbyteLogger


class Error(Exception):
    """ Base Error class for other exceptions """

    # Define the instance of the Native Airbyte Logger
    logger = AirbyteLogger()


class ZOQLQueryError(Error):
    """ Base class for  ZOQL EXPORT query errors """

    def __init__(self, response: requests.Response = None):
        if response:
            self.response = response.json()
            self.error_msg = self.response["data"]["errorMessage"]
            self.query = self.response["data"]["query"]
            super().__init__(self.logger.error(f"{self.error_msg}, QUERY: {self.query}"))
        # Exit with non-zero status
        sys.exit(1)


class ZOQLQueryFailed(ZOQLQueryError):
    """ Failed to execute query on the server side """


class ZOQLQueryFieldCannotResolve(Error):
    """
    Failed to execute query on the server side because of the certain field could not be resolved
    This exception is used to switch the default cursor_field inside the query.
    """

    def __init__(self, message: str = "Cursor 'UpdatedDate' is not available. Switching cursor to 'CreatedDate'"):
        super().__init__(self.logger.info(message))


class ZOQLQueryCannotProcessObject(Error):
    """
    The error raises when the user doesn't have the right permissions to read certain Zuora Object,
    or the object cannot be read due to technical reasons, we receive something like: 'failed to process object' msg,
    We trying to skip reading this stream, return [] as output and continue to read other streams
    """

    def __init__(
        self,
        message: str = "The stream cannot be processed, check Zuora Object's Permissions / Subscription Plan. This warning is not critical, and could be ignored.",
    ):
        super().__init__(self.logger.warn(message))
