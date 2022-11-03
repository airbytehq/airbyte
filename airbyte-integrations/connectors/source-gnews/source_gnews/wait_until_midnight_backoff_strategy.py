#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers import BackoffStrategy
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class WaitUntilMidnightBackoffStrategy(BackoffStrategy, JsonSchemaMixin):
    """
    Backoff strategy that waits until next midnight
    """

    def backoff(self, response: requests.Response, attempt_count: int) -> Optional[float]:
        now_utc = datetime.utcnow()
        midnight_utc = (now_utc + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        delta = midnight_utc - now_utc
        return delta.total_seconds() if type(delta) is timedelta else delta.seconds
