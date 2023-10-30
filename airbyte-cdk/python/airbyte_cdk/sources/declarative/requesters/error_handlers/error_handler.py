#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from dataclasses import dataclass
from typing import Union

import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_status import ResponseStatus


@dataclass
class ErrorHandler:
    """
    Defines whether a request was successful and how to handle a failure.
    """

    @property
    @abstractmethod
    def max_retries(self) -> Union[int, None]:
        """
        Specifies maximum amount of retries for backoff policy. Return None for no limit.
        """
        pass

    @property
    @abstractmethod
    def max_time(self) -> Union[int, None]:
        """
        Specifies maximum total waiting time (in seconds) for backoff policy. Return None for no limit.
        """
        pass

    @abstractmethod
    def interpret_response(self, response: requests.Response) -> ResponseStatus:
        """
        Evaluate response status describing whether a failing request should be retried or ignored.

        :param response: response to evaluate
        :return: response status
        """
        pass
