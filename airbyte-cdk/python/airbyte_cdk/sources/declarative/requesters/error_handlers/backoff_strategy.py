#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional

import requests
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class BackoffStrategy(JsonSchemaMixin):
    """
    Backoff strategy defining how long to wait before retrying a request that resulted in an error.
    """

    @abstractmethod
    def backoff(self, response: requests.Response, attempt_count: int) -> Optional[float]:
        """
        Return time to wait before retrying the request.
        :param response: response received for the request to retry
        :param attempt_count: number of attempts to submit the request
        :return: time to wait in seconds
        """
