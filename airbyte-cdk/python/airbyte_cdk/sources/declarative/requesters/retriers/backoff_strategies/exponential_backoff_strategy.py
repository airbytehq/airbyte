#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Optional

import requests
from airbyte_cdk.sources.declarative.requesters.retriers.backoff_strategy import BackoffStrategy
from pydantic import BaseModel


class ExponentialBackoffStrategy(BackoffStrategy, BaseModel):
    """
    Backoff strategy that uses exponential backoff.
    """


def backoff(self, response: requests.Response) -> Optional[float]:
    # Returning None backoff time makes the HttpStream use exponential backoff
    return None
