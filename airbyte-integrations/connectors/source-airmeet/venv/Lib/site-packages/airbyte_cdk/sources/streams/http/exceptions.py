#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Optional, Union

import requests

from airbyte_cdk.models import FailureType


class BaseBackoffException(requests.exceptions.HTTPError):
    def __init__(
        self,
        request: requests.PreparedRequest,
        response: Optional[Union[requests.Response, Exception]],
        error_message: str = "",
        failure_type: Optional[FailureType] = None,
    ):
        self.failure_type = failure_type
        if isinstance(response, requests.Response):
            error_message = (
                error_message
                or f"Request URL: {request.url}, Response Code: {response.status_code}, Response Text: {response.text}"
            )
            super().__init__(error_message, request=request, response=response)
        else:
            error_message = error_message or f"Request URL: {request.url}, Exception: {response}"
            super().__init__(error_message, request=request, response=None)


class RequestBodyException(Exception):
    """
    Raised when there are issues in configuring a request body
    """


class UserDefinedBackoffException(BaseBackoffException):
    """
    An exception that exposes how long it attempted to backoff
    """

    def __init__(
        self,
        backoff: Union[int, float],
        request: requests.PreparedRequest,
        response: Optional[Union[requests.Response, Exception]],
        error_message: str = "",
        failure_type: Optional[FailureType] = None,
    ):
        """
        :param backoff: how long to backoff in seconds
        :param request: the request that triggered this backoff exception
        :param response: the response that triggered the backoff exception
        """
        self.backoff = backoff
        super().__init__(
            request=request,
            response=response,
            error_message=error_message,
            failure_type=failure_type,
        )


class DefaultBackoffException(BaseBackoffException):
    pass


class RateLimitBackoffException(BaseBackoffException):
    pass
