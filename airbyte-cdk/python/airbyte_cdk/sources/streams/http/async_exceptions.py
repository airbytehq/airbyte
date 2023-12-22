#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Union

import aiohttp


class BaseBackoffException(aiohttp.ClientResponseError):
    def __init__(self, response: aiohttp.ClientResponse, error_message: str = ""):
        error_message = (
            error_message or f"Request URL: {response.request_info.url}, Response Code: {response.status}, Response Text: {response.text}"
        )
        super().__init__(request_info=response.request_info, history=(response,), status=response.status, message=error_message, headers=response.headers)


class RequestBodyException(Exception):
    """
    Raised when there are issues in configuring a request body
    """


class UserDefinedBackoffException(BaseBackoffException):
    """
    An exception that exposes how long it attempted to backoff
    """

    def __init__(self, backoff: Union[int, float], response: aiohttp.ClientResponse, error_message: str = ""):
        """
        :param backoff: how long to backoff in seconds
        :param request: the request that triggered this backoff exception
        :param response: the response that triggered the backoff exception
        """
        self.backoff = backoff
        super().__init__(response=response, error_message=error_message)


class DefaultBackoffException(BaseBackoffException):
    pass
