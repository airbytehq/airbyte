#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest

from components import ReportCreationRequester


def _create_requester(config, base_body):
    """Helper to create a ReportCreationRequester with a mocked parent body."""
    requester = ReportCreationRequester.__new__(ReportCreationRequester)
    requester.config = config
    requester._request_options_provider = MagicMock()
    requester._request_options_provider.get_request_body_json.return_value = base_body
    return requester


_BASE_BODY = {
    "reportType": "GET_LEDGER_SUMMARY_VIEW_DATA",
    "marketplaceIds": ["ATVPDKIKX0DER"],
    "dataStartTime": "2024-01-01T00:00:00Z",
    "dataEndTime": "2024-01-31T23:59:59Z",
}


@pytest.mark.parametrize(
    "config,base_body,expected_report_options",
    [
        pytest.param(
            {
                "report_options_list": [
                    {
                        "report_name": "GET_LEDGER_SUMMARY_VIEW_DATA",
                        "stream_name": "GET_LEDGER_SUMMARY_VIEW_DATA",
                        "options_list": [
                            {"option_name": "aggregatedByTimePeriod", "option_value": "DAILY"},
                            {"option_name": "aggregateByLocation", "option_value": "FC"},
                        ],
                    }
                ]
            },
            _BASE_BODY,
            {"aggregatedByTimePeriod": "DAILY", "aggregateByLocation": "FC"},
            id="injects_matching_options_from_config",
        ),
        pytest.param(
            {
                "report_options_list": [
                    {
                        "report_name": "GET_LEDGER_SUMMARY_VIEW_DATA",
                        "stream_name": "my_custom_stream_name",
                        "options_list": [
                            {"option_name": "aggregatedByTimePeriod", "option_value": "MONTHLY"},
                        ],
                    }
                ]
            },
            _BASE_BODY,
            {"aggregatedByTimePeriod": "MONTHLY"},
            id="matches_on_report_name_not_stream_name",
        ),
        pytest.param(
            {
                "report_options_list": [
                    {
                        "report_name": "GET_VENDOR_FORECASTING_REPORT",
                        "stream_name": "GET_VENDOR_FORECASTING_REPORT",
                        "options_list": [
                            {"option_name": "customOption", "option_value": "customValue"},
                            {"option_name": "sellingProgram", "option_value": "RETAIL"},
                        ],
                    }
                ]
            },
            {
                "reportType": "GET_VENDOR_FORECASTING_REPORT",
                "marketplaceIds": ["ATVPDKIKX0DER"],
                "reportOptions": {"sellingProgram": "FRESH"},
            },
            {"sellingProgram": "RETAIL", "customOption": "customValue"},
            id="user_config_overrides_hardcoded_options",
        ),
    ],
)
def test_report_options_injected(config, base_body, expected_report_options):
    requester = _create_requester(config, base_body)

    result = requester.get_request_body_json(stream_state=None, stream_slice=None, next_page_token=None)

    assert result["reportOptions"] == expected_report_options


@pytest.mark.parametrize(
    "config,base_body",
    [
        pytest.param(
            {
                "report_options_list": [
                    {
                        "report_name": "GET_LEDGER_SUMMARY_VIEW_DATA",
                        "stream_name": "GET_LEDGER_SUMMARY_VIEW_DATA",
                        "options_list": [{"option_name": "x", "option_value": "y"}],
                    }
                ]
            },
            {
                "reportType": "GET_FLAT_FILE_OPEN_LISTINGS_DATA",
                "marketplaceIds": ["ATVPDKIKX0DER"],
                "dataStartTime": "2024-01-01T00:00:00Z",
                "dataEndTime": "2024-01-31T23:59:59Z",
            },
            id="no_matching_report_name",
        ),
        pytest.param(
            {},
            _BASE_BODY,
            id="config_has_no_report_options_list_key",
        ),
        pytest.param(
            {"report_options_list": []},
            _BASE_BODY,
            id="config_has_empty_report_options_list",
        ),
        pytest.param(
            {"report_options_list": None},
            _BASE_BODY,
            id="config_has_none_report_options_list",
        ),
    ],
)
def test_report_options_not_injected(config, base_body):
    requester = _create_requester(config, base_body)

    result = requester.get_request_body_json(stream_state=None, stream_slice=None, next_page_token=None)

    assert "reportOptions" not in result
    assert result["reportType"] == base_body["reportType"]


def test_preserves_hardcoded_options_when_no_config_match():
    config = {
        "report_options_list": [
            {
                "report_name": "GET_LEDGER_SUMMARY_VIEW_DATA",
                "stream_name": "GET_LEDGER_SUMMARY_VIEW_DATA",
                "options_list": [{"option_name": "x", "option_value": "y"}],
            }
        ]
    }
    base_body = {
        "reportType": "GET_VENDOR_FORECASTING_REPORT",
        "marketplaceIds": ["ATVPDKIKX0DER"],
        "reportOptions": {"sellingProgram": "FRESH"},
    }
    requester = _create_requester(config, base_body)

    result = requester.get_request_body_json(stream_state=None, stream_slice=None, next_page_token=None)

    assert result["reportOptions"] == {"sellingProgram": "FRESH"}


def test_returns_none_when_parent_returns_none():
    config = {
        "report_options_list": [
            {
                "report_name": "GET_LEDGER_SUMMARY_VIEW_DATA",
                "stream_name": "GET_LEDGER_SUMMARY_VIEW_DATA",
                "options_list": [{"option_name": "x", "option_value": "y"}],
            }
        ]
    }
    requester = _create_requester(config, None)

    result = requester.get_request_body_json(stream_state=None, stream_slice=None, next_page_token=None)

    assert result is None


def test_handles_body_without_report_type():
    config = {
        "report_options_list": [
            {
                "report_name": "GET_LEDGER_SUMMARY_VIEW_DATA",
                "stream_name": "GET_LEDGER_SUMMARY_VIEW_DATA",
                "options_list": [{"option_name": "x", "option_value": "y"}],
            }
        ]
    }
    base_body = {"marketplaceIds": ["ATVPDKIKX0DER"]}
    requester = _create_requester(config, base_body)

    result = requester.get_request_body_json(stream_state=None, stream_slice=None, next_page_token=None)

    assert result == base_body
    assert "reportOptions" not in result
