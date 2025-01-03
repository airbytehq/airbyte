# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
from typing import Any, Optional, Union

import requests

from airbyte_cdk.sources.streams.http.error_handlers import BackoffStrategy


class AirtableBackoffStrategy(BackoffStrategy):
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def backoff_time(
        self, response_or_exception: Optional[Union[requests.Response, requests.RequestException]], **kwargs: Any
    ) -> Optional[float]:
        """
        Based on official docs: https://airtable.com/developers/web/api/rate-limits
        when 429 is received, we should wait at least 30 sec.
        """
        if isinstance(response_or_exception, requests.Response):
            if response_or_exception.status_code == 429:
                self.logger.error("Rate limited exceeded, waiting 30 seconds before retrying.")
                return 30
        return None
