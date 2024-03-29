# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import logging
from typing import Dict

import requests
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from requests import HTTPError


class HarvestAvailabilityStrategy(HttpAvailabilityStrategy):
    """
    This class is tested as part of test_source.check_connection
    """

    def reasons_for_unavailable_status_codes(
        self, stream: Stream, logger: logging.Logger, source: Source, error: HTTPError
    ) -> Dict[int, str]:
        reasons_for_codes: Dict[int, str] = {
            requests.codes.UNAUTHORIZED: "Please ensure your credentials are valid.",
            requests.codes.FORBIDDEN: "This is most likely due to insufficient permissions on the credentials in use.",
            requests.codes.NOT_FOUND: "Please ensure that your account ID is properly set. If it is the case and you are still seeing this error, please contact Airbyte support.",
        }
        return reasons_for_codes
