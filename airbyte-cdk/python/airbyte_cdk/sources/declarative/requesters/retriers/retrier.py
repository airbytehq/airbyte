#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Union

import requests


class NonRetriableBehavior(Enum):
    Ok = ("OK",)
    Fail = ("FAIL",)
    Ignore = "IGNORE"


RetryBehavior = Union[NonRetriableBehavior, Optional[float]]


class Retrier(ABC):
    @property
    @abstractmethod
    def max_retries(self) -> Union[int, None]:
        pass

    @abstractmethod
    def should_retry(self, response: requests.Response) -> RetryBehavior:
        pass

    @abstractmethod
    def backoff_time(self, response: requests.Response) -> Optional[float]:
        pass
