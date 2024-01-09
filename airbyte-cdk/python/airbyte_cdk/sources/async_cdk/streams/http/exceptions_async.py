#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Union

from airbyte_cdk.sources.streams.http.utils import HttpError
from airbyte_cdk.sources.streams.http.exceptions import AbstractBaseBackoffException


class AsyncBaseBackoffException(AbstractBaseBackoffException, HttpError):
    def __init__(self, error: HttpError, error_message: str = ""):
        error_message = (
            error_message
            or f"Request URL: {error.url}, Response Code: {error.status_code}, Response Text: {error.text}"
        )
        super().__init__(aiohttp_error=error._aiohttp_error, error_message=error_message)


class AsyncUserDefinedBackoffException(AsyncBaseBackoffException):
    """
    An exception that exposes how long it attempted to backoff
    """

    def __init__(
        self,
        backoff: Union[int, float],
        error: HttpError,
        error_message: str = "",
    ):
        """
        :param backoff: how long to backoff in seconds
        :param request: the request that triggered this backoff exception
        :param response: the response that triggered the backoff exception
        """
        self.backoff = backoff
        super().__init__(error, error_message=error_message)


class AsyncDefaultBackoffException(AsyncBaseBackoffException):
    pass
