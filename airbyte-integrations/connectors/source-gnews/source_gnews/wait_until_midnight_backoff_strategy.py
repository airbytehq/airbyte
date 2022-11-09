#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from datetime import datetime, timedelta
from typing import Any, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers import BackoffStrategy
from airbyte_cdk.sources.declarative.types import Config
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class WaitUntilMidnightBackoffStrategy(BackoffStrategy, JsonSchemaMixin):
    """
    Backoff strategy that waits until next midnight
    """

    options: InitVar[Mapping[str, Any]]
    config: Config

    def backoff(self, response: requests.Response, attempt_count: int) -> Optional[float]:
        now_utc = datetime.utcnow()
        midnight_utc = (now_utc + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        delta = midnight_utc - now_utc
        return delta.total_seconds() if type(delta) is timedelta else delta.seconds
