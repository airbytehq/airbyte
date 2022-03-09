#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.parse import unquote

import pendulum
import pytest
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.streams.http.auth import NoAuth
from freezegun import freeze_time
from source_google_analytics_v4.source import (
    DATA_IS_NOT_GOLDEN_MSG,
    RESULT_IS_SAMPLED_MSG,
    GoogleAnalyticsV4IncrementalObjectsBase,
    GoogleAnalyticsV4Stream,
    GoogleAnalyticsV4TypesList,
    SourceGoogleAnalyticsV4,
)


def read_file(file_name):
    parent_location = Path(__file__).absolute().parent
    file = open(parent_location / file_name).read()
    return file


expected_metrics_dimensions_type_map = (
    {"ga:users": "INTEGER", "ga:newUsers": "INTEGER"},
    {"ga:date": "STRING", "ga:country": "STRING"},
)


@pytest.fixture
def mock_metrics_dimensions_type_list_link(requests_mock):
    requests_mock.get(
        "https://www.googleapis.com/analytics/v3/metadata/ga/columns",
        json=json.loads(read_file("metrics_dimensions_type_list.json")),
    )


@pytest.fixture
def mock_auth_call(requests_mock):
    yield requests_mock.post(
        "https://oauth2.googleapis.com/token",
        json={"access_token": "", "expires_in": 0},
    )


@pytest.fixture
def mock_auth_check_connection(requests_mock):
    yield requests_mock.post(
        "https://analyticsreporting.googleapis.com/v4/reports:batchGet",
        json={"data": {"test": "value"}},
    )


@pytest.fixture
def mock_unknown_metrics_or_dimensions_error(requests_mock):
    yield requests_mock.post(
        "https://analyticsreporting.googleapis.com/v4/reports:batchGet",
        status_code=400,
        json={"error": {"message": "Unknown metrics or dimensions"}},
    )


@pytest.fixture
def mock_api_returns_no_records(requests_mock):
    """API returns empty data for given date based slice"""
    yield requests_mock.post(
        "https://analyticsreporting.googleapis.com/v4/reports:batchGet",
        json=json.loads(read_file("empty_response.json")),
    )


@pytest.fixture
def mock_api_returns_valid_records(requests_mock):
    """API returns valid data for given date based slice"""
    yield requests_mock.post(
        "https://analyticsreporting.googleapis.com/v4/reports:batchGet",
        json=json.loads(read_file("response_with_records.json")),
    )


@pytest.fixture
def mock_api_returns_sampled_results(requests_mock):
    """API returns valid data for given date based slice"""
    yield requests_mock.post(
        "https://analyticsreporting.googleapis.com/v4/reports:batchGet",
        json=json.loads(read_file("response_with_sampling.json")),
    )


@pytest.fixture
def mock_api_returns_is_data_golden_false(requests_mock):
    """API returns valid data for given date based slice"""
    yield requests_mock.post(
        "https://analyticsreporting.googleapis.com/v4/reports:batchGet",
        json=json.loads(read_file("response_is_data_golden_false.json")),
    )


@pytest.fixture()
def test_config():
    test_config = json.loads(read_file("../integration_tests/sample_config.json"))
    test_config["authenticator"] = NoAuth()
    test_config["metrics"] = []
    test_config["dimensions"] = []
    test_config["credentials"] = {
        "type": "Service",
    }
    return test_config


def test_metrics_dimensions_type_list(mock_metrics_dimensions_type_list_link):
    test_metrics, test_dimensions = GoogleAnalyticsV4TypesList().read_records(sync_mode=None)

    assert test_metrics, test_dimensions == expected_metrics_dimensions_type_map


def get_metrics_dimensions_mapping():
    test_metrics_dimensions_map = {
        "metric": [("ga:users", "integer"), ("ga:newUsers", "integer")],
        "dimension": [("ga:dimension", "string")],
    }
    for field_type, attribute_expected_pairs in test_metrics_dimensions_map.items():
        for attribute_expected_pair in attribute_expected_pairs:
            attribute, expected = attribute_expected_pair
            yield field_type, attribute, expected


@pytest.mark.parametrize("metrics_dimensions_mapping", get_metrics_dimensions_mapping())
def test_lookup_metrics_dimensions_data_type(test_config, metrics_dimensions_mapping, mock_metrics_dimensions_type_list_link):
    field_type, attribute, expected = metrics_dimensions_mapping
    g = GoogleAnalyticsV4Stream(config=test_config)
    test = g.lookup_data_type(field_type, attribute)
    assert test == expected


def test_data_is_not_golden_is_logged_as_warning(
    mock_api_returns_is_data_golden_false,
    test_config,
    mock_metrics_dimensions_type_list_link,
    mock_auth_call,
    caplog,
):
    source = SourceGoogleAnalyticsV4()
    del test_config["custom_reports"]
    catalog = ConfiguredAirbyteCatalog.parse_obj(json.loads(read_file("./configured_catalog.json")))
    list(source.read(logging.getLogger(), test_config, catalog))
    assert DATA_IS_NOT_GOLDEN_MSG in caplog.text


def test_sampled_result_is_logged_as_warning(
    mock_api_returns_sampled_results,
    test_config,
    mock_metrics_dimensions_type_list_link,
    mock_auth_call,
    caplog,
):
    source = SourceGoogleAnalyticsV4()
    del test_config["custom_reports"]
    catalog = ConfiguredAirbyteCatalog.parse_obj(json.loads(read_file("./configured_catalog.json")))
    list(source.read(logging.getLogger(), test_config, catalog))
    assert RESULT_IS_SAMPLED_MSG in caplog.text


def test_no_regressions_for_result_is_sampled_and_data_is_golden_warnings(
    mock_api_returns_valid_records,
    test_config,
    mock_metrics_dimensions_type_list_link,
    mock_auth_call,
    caplog,
):
    source = SourceGoogleAnalyticsV4()
    del test_config["custom_reports"]
    catalog = ConfiguredAirbyteCatalog.parse_obj(json.loads(read_file("./configured_catalog.json")))
    list(source.read(logging.getLogger(), test_config, catalog))
    assert RESULT_IS_SAMPLED_MSG not in caplog.text
    assert DATA_IS_NOT_GOLDEN_MSG not in caplog.text


@patch("source_google_analytics_v4.source.jwt")
def test_check_connection_fails_jwt(
    jwt_encode_mock,
    mocker,
    mock_metrics_dimensions_type_list_link,
    mock_auth_call,
    mock_api_returns_no_records,
):
    """
    check_connection fails because of the API returns no records,
    then we assume than user doesn't have permission to read requested `view`
    """
    test_config = json.loads(read_file("../integration_tests/sample_config.json"))
    del test_config["custom_reports"]
    test_config["credentials"] = {
        "auth_type": "Service",
        "credentials_json": '{"client_email": "", "private_key": "", "private_key_id": ""}',
    }
    source = SourceGoogleAnalyticsV4()
    is_success, msg = source.check_connection(MagicMock(), test_config)
    assert is_success is False
    assert (
        msg == f"Please check the permissions for the requested view_id: {test_config['view_id']}. Cannot retrieve data from that view ID."
    )
    jwt_encode_mock.encode.assert_called()
    assert mock_auth_call.called
    assert mock_api_returns_no_records.called


@patch("source_google_analytics_v4.source.jwt")
def test_check_connection_success_jwt(
    jwt_encode_mock,
    mocker,
    mock_metrics_dimensions_type_list_link,
    mock_auth_call,
    mock_api_returns_valid_records,
):
    """
    check_connection succeeds because of the API returns valid records for the latest date based slice,
    then we assume than user has permission to read requested `view`
    """
    test_config = json.loads(read_file("../integration_tests/sample_config.json"))
    del test_config["custom_reports"]
    test_config["credentials"] = {
        "auth_type": "Service",
        "credentials_json": '{"client_email": "", "private_key": "", "private_key_id": ""}',
    }
    source = SourceGoogleAnalyticsV4()
    is_success, msg = source.check_connection(MagicMock(), test_config)
    assert is_success is True
    assert msg is None
    jwt_encode_mock.encode.assert_called()
    assert mock_auth_call.called
    assert mock_api_returns_valid_records.called


@patch("source_google_analytics_v4.source.jwt")
def test_check_connection_fails_oauth(
    jwt_encode_mock,
    mocker,
    mock_metrics_dimensions_type_list_link,
    mock_auth_call,
    mock_api_returns_no_records,
):
    """
    check_connection fails because of the API returns no records,
    then we assume than user doesn't have permission to read requested `view`
    """
    test_config = json.loads(read_file("../integration_tests/sample_config.json"))
    del test_config["custom_reports"]
    test_config["credentials"] = {
        "auth_type": "Client",
        "client_id": "client_id_val",
        "client_secret": "client_secret_val",
        "refresh_token": "refresh_token_val",
    }
    source = SourceGoogleAnalyticsV4()
    is_success, msg = source.check_connection(MagicMock(), test_config)
    assert is_success is False
    assert (
        msg == f"Please check the permissions for the requested view_id: {test_config['view_id']}. Cannot retrieve data from that view ID."
    )
    jwt_encode_mock.encode.assert_not_called()
    assert "https://www.googleapis.com/auth/analytics.readonly" in unquote(mock_auth_call.last_request.body)
    assert "client_id_val" in unquote(mock_auth_call.last_request.body)
    assert "client_secret_val" in unquote(mock_auth_call.last_request.body)
    assert "refresh_token_val" in unquote(mock_auth_call.last_request.body)
    assert mock_auth_call.called
    assert mock_api_returns_no_records.called


@patch("source_google_analytics_v4.source.jwt")
def test_check_connection_success_oauth(
    jwt_encode_mock,
    mocker,
    mock_metrics_dimensions_type_list_link,
    mock_auth_call,
    mock_api_returns_valid_records,
):
    """
    check_connection succeeds because of the API returns valid records for the latest date based slice,
    then we assume than user has permission to read requested `view`
    """
    test_config = json.loads(read_file("../integration_tests/sample_config.json"))
    del test_config["custom_reports"]
    test_config["credentials"] = {
        "auth_type": "Client",
        "client_id": "client_id_val",
        "client_secret": "client_secret_val",
        "refresh_token": "refresh_token_val",
    }
    source = SourceGoogleAnalyticsV4()
    is_success, msg = source.check_connection(MagicMock(), test_config)
    assert is_success is True
    assert msg is None
    jwt_encode_mock.encode.assert_not_called()
    assert "https://www.googleapis.com/auth/analytics.readonly" in unquote(mock_auth_call.last_request.body)
    assert "client_id_val" in unquote(mock_auth_call.last_request.body)
    assert "client_secret_val" in unquote(mock_auth_call.last_request.body)
    assert "refresh_token_val" in unquote(mock_auth_call.last_request.body)
    assert mock_auth_call.called
    assert mock_api_returns_valid_records.called


def test_unknown_metrics_or_dimensions_error_validation(mock_metrics_dimensions_type_list_link, mock_unknown_metrics_or_dimensions_error):
    records = GoogleAnalyticsV4Stream(MagicMock()).read_records(sync_mode=None)
    assert records


@freeze_time("2021-11-30")
def test_stream_slices_limited_by_current_date(test_config):
    g = GoogleAnalyticsV4IncrementalObjectsBase(config=test_config)
    stream_state = {"ga_date": "2050-05-01"}
    slices = g.stream_slices(stream_state=stream_state)
    current_date = pendulum.now().date().strftime("%Y-%m-%d")

    assert len(slices) == 1
    assert slices[0]["startDate"] == slices[0]["endDate"]
    assert slices[0]["endDate"] == current_date


@freeze_time("2021-11-30")
def test_stream_slices_start_from_current_date_if_abnornal_state_is_passed(test_config):
    g = GoogleAnalyticsV4IncrementalObjectsBase(config=test_config)
    stream_state = {"ga_date": "2050-05-01"}
    slices = g.stream_slices(stream_state=stream_state)
    current_date = pendulum.now().date().strftime("%Y-%m-%d")

    assert len(slices) == 1
    assert slices[0]["startDate"] == slices[0]["endDate"]
    assert slices[0]["startDate"] == current_date
