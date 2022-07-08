#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from typing import Optional

import requests


class BackoffStrategy:
    @abstractmethod
    def backoff(self, response: requests.Response, attempt_count: int) -> Optional[float]:
        pass
