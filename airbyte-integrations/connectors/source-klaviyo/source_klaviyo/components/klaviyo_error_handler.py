# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Optional, Union

import requests
from requests.exceptions import InvalidURL

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers import ErrorResolution, ResponseAction


class KlaviyoErrorHandler(DefaultErrorHandler):
    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]]) -> ErrorResolution:
        """
        We have seen `[Errno -3] Temporary failure in name resolution` a couple of times on two different connections
        (1fed2ede-2d33-4543-85e3-7d6e5736075d and 1b276f7d-358a-4fe3-a437-6747fd780eed). Retrying the requests on later syncs is working
        which makes it sound like a transient issue.
        """
        if isinstance(response_or_exception, InvalidURL):
            return ErrorResolution(
                response_action=ResponseAction.RETRY,
                failure_type=FailureType.transient_error,
                error_message="source-klaviyo has faced a temporary DNS resolution issue. Retrying...",
            )
        return super().interpret_response(response_or_exception)
