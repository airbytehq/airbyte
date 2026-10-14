#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import re
from dataclasses import InitVar, dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Optional, Union

import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.error_handlers import BackoffStrategy
from airbyte_cdk.sources.types import Config
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


@dataclass
class GmailRetryAfterFromBodyBackoffStrategy(BackoffStrategy):
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    max_waiting_time_in_seconds: Optional[float] = None

    def backoff_time(
        self,
        response_or_exception: Optional[Union[requests.Response, requests.RequestException]],
        attempt_count: int,
    ) -> Optional[float]:
        if not isinstance(response_or_exception, requests.Response):
            return None

        match = re.search(
            r"Retry after (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z)",
            response_or_exception.text,
        )
        if not match:
            return None

        retry_at_text = match.group(1)
        retry_at = datetime.fromisoformat(retry_at_text.replace("Z", "+00:00"))
        wait = (retry_at - datetime.now(timezone.utc)).total_seconds()
        if wait <= 0:
            return 1.0

        if self.max_waiting_time_in_seconds is not None and wait >= self.max_waiting_time_in_seconds:
            cap = f"{self.max_waiting_time_in_seconds:g}"
            raise AirbyteTracedException(
                failure_type=FailureType.transient_error,
                message=(
                    f"Gmail rate limit for this account resets at {retry_at_text}, which is longer than "
                    f"the connector waits ({cap} s). The sync will retry on its next attempt."
                ),
                internal_message=(f"Gmail Retry after time {retry_at_text} exceeds the configured wait cap of {cap} seconds."),
            )

        return wait
