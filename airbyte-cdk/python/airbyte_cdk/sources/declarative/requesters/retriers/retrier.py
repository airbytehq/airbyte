#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union

import requests


class NonRetriableResponseStatus(Enum):
    Ok = ("OK",)
    FAIL = ("FAIL",)
    IGNORE = ("IGNORE",)


@dataclass
class RetryResponseStatus:
    retry_in: Optional[float]


ResponseStatus = Union[NonRetriableResponseStatus, RetryResponseStatus]


class Retrier(ABC):
    @property
    @abstractmethod
    def max_retries(self) -> Union[int, None]:
        pass

    @property
    @abstractmethod
    def retry_factor(self) -> float:
        pass

    @abstractmethod
    def should_retry(self, response: requests.Response) -> ResponseStatus:
        pass
