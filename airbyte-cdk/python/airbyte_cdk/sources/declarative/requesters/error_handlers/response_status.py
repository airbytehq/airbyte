#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Final, Optional, Union

from airbyte_cdk.sources.declarative.requesters.error_handlers.response_action import ResponseAction


class ResponseStatus:
    """
    ResponseAction amended with backoff time if an action is RETRY
    """

    def __init__(self, response_action: Union[ResponseAction, str], retry_in: Optional[float] = None, error_message: str = ""):
        """
        :param response_action: response action to execute
        :param retry_in: backoff time (if action is RETRY)
        :param error_message: the error to be displayed back to the customer
        """
        if isinstance(response_action, str):
            response_action = ResponseAction[response_action]
        if retry_in and response_action != ResponseAction.RETRY:
            raise ValueError(f"Unexpected backoff time ({retry_in} for non-retryable response action {response_action}")
        self._retry_in = retry_in
        self._action = response_action
        self._error_message = error_message

    @property
    def action(self):
        """The ResponseAction to execute when a response matches the filter"""
        return self._action

    @property
    def retry_in(self) -> Optional[float]:
        """How long to backoff before retrying a response. None if no wait required."""
        return self._retry_in

    @property
    def error_message(self) -> str:
        """The message to be displayed when an error response is received"""
        return self._error_message

    @classmethod
    def retry(cls, retry_in: Optional[float]) -> "ResponseStatus":
        """
        Returns a ResponseStatus defining how long to backoff before retrying

        :param retry_in: how long to backoff before retrying. None if no wait required
        :return: A response status defining how long to backoff before retrying
        """
        return ResponseStatus(ResponseAction.RETRY, retry_in)

    def __eq__(self, other):
        if not other:
            return not self
        return self.action == other.action and self.retry_in == other.retry_in

    def __hash__(self):
        return hash([self.action, self.retry_in])


"""Response is successful. No need to retry"""
SUCCESS: Final[ResponseStatus] = ResponseStatus(ResponseAction.SUCCESS)
"""Response is unsuccessful. The failure needs to be handled"""
FAIL: Final[ResponseStatus] = ResponseStatus(ResponseAction.FAIL)
"""Response is unsuccessful, but can be ignored. No need to retry"""
IGNORE: Final[ResponseStatus] = ResponseStatus(ResponseAction.IGNORE)
