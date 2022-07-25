#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Final, Optional, Union

from airbyte_cdk.sources.declarative.requesters.error_handlers.response_action import ResponseAction


class ResponseStatus:
    """
    ResponseAction amended with backoff time if a action is RETRY
    """

    def __init__(self, response_action: Union[ResponseAction, str], retry_in: Optional[float] = None):
        """
        :param response_action: response action to execute
        :param retry_in: backoff time (if action is RETRY)
        """
        if isinstance(response_action, str):
            response_action = ResponseAction[response_action]
        if retry_in and response_action != ResponseAction.RETRY:
            raise ValueError(f"Unexpected backoff time ({retry_in} for non-retryable response action {response_action}")
        self._retry_in = retry_in
        self._action = response_action

    @property
    def action(self):
        return self._action

    @property
    def retry_in(self) -> Optional[float]:
        return self._retry_in

    @classmethod
    def retry(cls, retry_in: Optional[float]):
        return ResponseStatus(ResponseAction.RETRY, retry_in)

    def __eq__(self, other):
        if not other:
            return not self
        return self.action == other.action and self.retry_in == other.retry_in

    def __hash__(self):
        return hash([self.action, self.retry_in])


SUCCESS: Final[ResponseStatus] = ResponseStatus(ResponseAction.SUCCESS)
FAIL: Final[ResponseStatus] = ResponseStatus(ResponseAction.FAIL)
IGNORE: Final[ResponseStatus] = ResponseStatus(ResponseAction.IGNORE)
