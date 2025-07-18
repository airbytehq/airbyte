#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Optional, Union

from requests import RequestException, Response

from airbyte_cdk.sources.streams.http.error_handlers import BackoffStrategy


class SlackBackoffStrategy(BackoffStrategy):
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def backoff_time(self, response_or_exception: Optional[Union[Response, RequestException]], **kwargs) -> Optional[float]:
        """
        This method is called if we run into the rate limit.
        Slack puts the retry time in the `Retry-After` response header so we
        we return that value. If the response is anything other than a 429 (e.g: 5XX)
        fall back on default retry behavior.
        Rate Limits Docs: https://api.slack.com/docs/rate-limits#web
        """
        if isinstance(response_or_exception, Response) and "Retry-After" in response_or_exception.headers:
            return int(response_or_exception.headers["Retry-After"])
        else:
            self.logger.info("Retry-after header not found. Using default backoff value")
            return 5
