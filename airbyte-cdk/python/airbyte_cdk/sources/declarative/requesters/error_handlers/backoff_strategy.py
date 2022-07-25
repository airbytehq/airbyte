#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from typing import Optional

import requests


class BackoffStrategy:
    @abstractmethod
    def backoff(self, response: requests.Response, attempt_count: int) -> Optional[float]:
        """
        Return time to wait before retrying the request.
        :param response: response received for the request to retry
        :param attempt_count: number of attempts to submit the request
        :return: time to wait in seconds
        """
