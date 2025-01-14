#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from unittest.mock import MagicMock

import pytest
from requests import Response
from source_airtable.airtable_backoff_strategy import AirtableBackoffStrategy


@pytest.mark.parametrize("response_code, expected_backoff_time", [(429, 30), (404, None)])
def test_backoff_time(response_code, expected_backoff_time):
    mocked_logger = MagicMock(spec=logging.Logger)
    backoff = AirtableBackoffStrategy(logger=mocked_logger)
    response = MagicMock(spec=Response)
    response.status_code = response_code
    assert backoff.backoff_time(response) == expected_backoff_time
