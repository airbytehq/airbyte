#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import httpx
import pytest
import respx
from source_exact.source import SourceExact


# @respx.mock
# def test_check_connection_ok():
#     source = SourceExact()
#     logger_mock, config_mock = MagicMock(), MagicMock()
#
#     respx.get("https://start.exactonline.nl/api/v1/sync/Financial/TransactionLines").mock(
#         return_value=httpx.Response(
#             200
#             , json={"unit": "test"}
#             )
#         )
#     assert source.check_connection(logger_mock, config_mock) == (True, None)


# TODO: enable again after fixing the issue with the refresh token in source.py
# def test_check_connection_failure_forbidden(requests_mock):
#     source = SourceExact()
#     logger_mock, config_mock = MagicMock(), MagicMock()

#     requests_mock.get("https://start.exactonline.nl/api/v1/current/Me", status_code=401)
#     assert source.check_connection(logger_mock, config_mock) == (
#         False,
#         "Exception happened during connection check. Validate that the access_token is still valid at this point. Details\n401 Client Error: None for url: https://start.exactonline.nl/api/v1/current/Me",
#     )


@pytest.mark.parametrize(
    "config",
    [
        None,
        {},
        {"credentials": {}},
        {"credentials": {"access_token": "missing refresh"}},
        {"credentials": {"refresh_token": "missing access"}},
    ],
)
def test_check_connection_failure_missing_credentials(config):
    source = SourceExact()
    logger_mock = MagicMock()

    assert source.check_connection(logger_mock, config) == (False, "Missing access or refresh token")
