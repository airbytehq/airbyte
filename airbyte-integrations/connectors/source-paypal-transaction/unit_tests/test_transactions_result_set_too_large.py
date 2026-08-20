# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from typing import Any, Dict, List
from unittest import TestCase

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_STREAM_NAME = "transactions"
_TOKEN_URL = "https://api-m.paypal.com/v1/oauth2/token"
_TRANSACTIONS_URL = "https://api-m.paypal.com/v1/reporting/transactions"
# A one-day time window over a two-day date range gives two partitions.
_START_DATE = "2024-01-01T00:00:00Z"
_END_DATE = "2024-01-03T00:00:00Z"
_FIRST_WINDOW = ("2024-01-01T00:00:00Z", "2024-01-01T23:59:59Z")
_FIRST_WINDOW_FIRST_HALF = ("2024-01-01T00:00:00Z", "2024-01-01T11:59:59Z")
_FIRST_WINDOW_SECOND_HALF = ("2024-01-01T12:00:00Z", "2024-01-01T23:59:59Z")
_SECOND_WINDOW = ("2024-01-02T00:00:00Z", "2024-01-03T00:00:00Z")
_ONE_SECOND_WINDOW = ("2024-01-01T00:00:00Z", "2024-01-01T00:00:01Z")

_RESULT_SET_TOO_LARGE_RESPONSE = HttpResponse(
    json.dumps(
        {
            "name": "RESULTSET_TOO_LARGE",
            "message": "Result set size is greater than the maximum limit. Change the filter criteria and try again.",
            "debug_id": "a-debug-id",
            "maximum_items": 10000,
        }
    ),
    status_code=400,
)


def _config(end_date: str = _END_DATE) -> Dict[str, Any]:
    return {
        "client_id": "a-client-id",
        "client_secret": "a-client-secret",
        "start_date": _START_DATE,
        "end_date": end_date,
        "is_sandbox": False,
        "time_window": 1,
    }


def _transactions_request(start_date: str, end_date: str) -> HttpRequest:
    return HttpRequest(
        url=_TRANSACTIONS_URL,
        query_params={
            "fields": "all",
            "start_date": start_date,
            "end_date": end_date,
            "page_size": "500",
        },
    )


def _transactions_response(transaction_ids: List[str], updated_date: str = "2024-01-01T05:00:00+0000") -> HttpResponse:
    return HttpResponse(
        json.dumps(
            {
                "transaction_details": [
                    {
                        "transaction_info": {
                            "transaction_id": transaction_id,
                            "transaction_updated_date": updated_date,
                        }
                    }
                    for transaction_id in transaction_ids
                ],
                "total_pages": 1,
            }
        )
    )


def _mock_authentication(http_mocker: HttpMocker) -> None:
    http_mocker.post(
        HttpRequest(url=_TOKEN_URL, body="grant_type=client_credentials&Content-Type=application%2Fx-www-form-urlencoded"),
        HttpResponse(json.dumps({"access_token": "an-access-token", "expires_in": 3600})),
    )


def _read(config: Dict[str, Any], expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
    source = YamlDeclarativeSource(config=config, catalog=catalog, state=None, path_to_yaml=str(_MANIFEST_PATH))
    return read(source, config, catalog, None, expecting_exception)


def _final_cursor_state(output: EntrypointOutput) -> Dict[str, Any]:
    return output.state_messages[-1].state.stream.stream_state.__dict__


class ResultSetTooLargeTest(TestCase):
    @HttpMocker()
    def test_given_result_set_too_large_when_read_then_read_halves_of_the_window(self, http_mocker: HttpMocker) -> None:
        _mock_authentication(http_mocker)
        http_mocker.get(_transactions_request(*_FIRST_WINDOW), _RESULT_SET_TOO_LARGE_RESPONSE)
        http_mocker.get(_transactions_request(*_FIRST_WINDOW_FIRST_HALF), _transactions_response(["first-half"]))
        http_mocker.get(_transactions_request(*_FIRST_WINDOW_SECOND_HALF), _transactions_response(["second-half"]))
        http_mocker.get(
            _transactions_request(*_SECOND_WINDOW),
            _transactions_response(["second-window"], updated_date="2024-01-02T05:00:00+0000"),
        )

        output = _read(_config())

        assert sorted(record.record.data["transaction_id"] for record in output.records) == [
            "first-half",
            "second-half",
            "second-window",
        ]
        assert not output.errors
        assert _final_cursor_state(output)["transaction_updated_date"] == "2024-01-02T05:00:00Z"

    @HttpMocker()
    def test_given_result_set_too_large_for_smallest_window_when_read_then_config_error(self, http_mocker: HttpMocker) -> None:
        _mock_authentication(http_mocker)
        http_mocker.get(_transactions_request(*_ONE_SECOND_WINDOW), _RESULT_SET_TOO_LARGE_RESPONSE)

        output = _read(_config(end_date=_ONE_SECOND_WINDOW[1]), expecting_exception=True)

        assert output.errors
        assert output.errors[-1].trace.error.failure_type == FailureType.config_error
