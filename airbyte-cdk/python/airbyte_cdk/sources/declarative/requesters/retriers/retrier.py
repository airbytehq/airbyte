#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Optional, Union

import requests


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
    def should_retry(self, response: requests.Response) -> bool:
        pass

    @abstractmethod
    def backoff_time(self, response: requests.Response) -> Optional[float]:
        pass
