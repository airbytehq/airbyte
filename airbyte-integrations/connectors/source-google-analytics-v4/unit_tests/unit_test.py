#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import copy
import json
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.parse import unquote

import pendulum
import pytest
from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode, Type
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
    response = json.loads(read_file("response_golden_data.json"))
    for report in response["reports"]:
        assert report["data"]["isDataGolden"] is True
    yield requests_mock.post("https://analyticsreporting.googleapis.com/v4/reports:batchGet", json=response)


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
    response = json.loads(read_file("response_non_golden_data.json"))
    for report in response["reports"]:
        assert "isDataGolden" not in report["data"]
    yield requests_mock.post("https://analyticsreporting.googleapis.com/v4/reports:batchGet", json=response)


@pytest.fixture
def configured_catalog():
    return ConfiguredAirbyteCatalog.parse_obj(json.loads(read_file("./configured_catalog.json")))


@pytest.fixture()
def test_config():
    test_conf = {
        "view_id": "1234567",
        "window_in_days": 1,
        "authenticator": NoAuth(),
        "metrics": [],
        "start_date": pendulum.now().subtract(days=2).date().strftime("%Y-%m-%d"),
        "dimensions": [],
        "credentials": {
            "auth_type": "Client",
            "client_id": "client_id_val",
            "client_secret": "client_secret_val",
            "refresh_token": "refresh_token_val",
        },
    }
    return copy.deepcopy(test_conf)


@pytest.fixture()
def test_config_auth_service(test_config):
    test_config["credentials"] = {
        "auth_type": "Service",
        "credentials_json": '{"client_email": "", "private_key": "", "private_key_id": ""}',
    }
    return copy.deepcopy(test_config)


def test_metrics_dimensions_type_list(mock_metrics_dimensions_type_list_link):
    test_metrics, test_dimensions = GoogleAnalyticsV4TypesList().read_records(sync_mode=None)

    assert test_metrics, test_dimensions == expected_metrics_dimensions_type_map


def get_metrics_dimensions_mapping():
    test_metrics_dimensions_map = {
        "metric": [("ga:users", "integer"), ("ga:newUsers", "integer")],
        "dimension": [("ga:dimension", "string"), ("ga:dateHourMinute", "integer")],
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
    configured_catalog,
    mock_metrics_dimensions_type_list_link,
    mock_auth_call,
    caplog,
):
    source = SourceGoogleAnalyticsV4()
    list(source.read(logging.getLogger(), test_config, configured_catalog))
    assert DATA_IS_NOT_GOLDEN_MSG in caplog.text


def test_sampled_result_is_logged_as_warning(
    mock_api_returns_sampled_results,
    test_config,
    configured_catalog,
    mock_metrics_dimensions_type_list_link,
    mock_auth_call,
    caplog,
):
    source = SourceGoogleAnalyticsV4()
    list(source.read(logging.getLogger(), test_config, configured_catalog))
    assert RESULT_IS_SAMPLED_MSG in caplog.text


def test_no_regressions_for_result_is_sampled_and_data_is_golden_warnings(
    mock_api_returns_valid_records,
    test_config,
    configured_catalog,
    mock_metrics_dimensions_type_list_link,
    mock_auth_call,
    caplog,
):
    source = SourceGoogleAnalyticsV4()
    list(source.read(logging.getLogger(), test_config, configured_catalog))
    assert RESULT_IS_SAMPLED_MSG not in caplog.text
    assert DATA_IS_NOT_GOLDEN_MSG not in caplog.text


@patch("source_google_analytics_v4.source.jwt")
def test_check_connection_fails_jwt(
    jwt_encode_mock,
    test_config_auth_service,
    mocker,
    mock_metrics_dimensions_type_list_link,
    mock_auth_call,
    mock_api_returns_no_records,
):
    """
    check_connection fails because of the API returns no records,
    then we assume than user doesn't have permission to read requested `view`
    """
    source = SourceGoogleAnalyticsV4()
    is_success, msg = source.check_connection(MagicMock(), test_config_auth_service)
    assert is_success is False
    assert (
        msg
        == f"Please check the permissions for the requested view_id: {test_config_auth_service['view_id']}. Cannot retrieve data from that view ID."
    )
    jwt_encode_mock.encode.assert_called()
    assert mock_auth_call.called
    assert mock_api_returns_no_records.called


@patch("source_google_analytics_v4.source.jwt")
def test_check_connection_success_jwt(
    jwt_encode_mock,
    test_config_auth_service,
    mocker,
    mock_metrics_dimensions_type_list_link,
    mock_auth_call,
    mock_api_returns_valid_records,
):
    """
    check_connection succeeds because of the API returns valid records for the latest date based slice,
    then we assume than user has permission to read requested `view`
    """
    source = SourceGoogleAnalyticsV4()
    is_success, msg = source.check_connection(MagicMock(), test_config_auth_service)
    assert is_success is True
    assert msg is None
    jwt_encode_mock.encode.assert_called()
    assert mock_auth_call.called
    assert mock_api_returns_valid_records.called


@patch("source_google_analytics_v4.source.jwt")
def test_check_connection_fails_oauth(
    jwt_encode_mock,
    test_config,
    mocker,
    mock_metrics_dimensions_type_list_link,
    mock_auth_call,
    mock_api_returns_no_records,
):
    """
    check_connection fails because of the API returns no records,
    then we assume than user doesn't have permission to read requested `view`
    """
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
    test_config,
    mocker,
    mock_metrics_dimensions_type_list_link,
    mock_auth_call,
    mock_api_returns_valid_records,
):
    """
    check_connection succeeds because of the API returns valid records for the latest date based slice,
    then we assume than user has permission to read requested `view`
    """
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
def test_stream_slice_limits(test_config, mock_metrics_dimensions_type_list_link):
    test_config["window_in_days"] = 14
    g = GoogleAnalyticsV4IncrementalObjectsBase(config=test_config)
    stream_state = {"ga_date": "2021-11-25"}
    slices = g.stream_slices(stream_state=stream_state)
    current_date = pendulum.now().date().strftime("%Y-%m-%d")
    expected_start_date = "2021-11-24"  # always resync two days back
    expected_end_date = current_date  # do not try to sync future dates
    assert slices == [{"startDate": expected_start_date, "endDate": expected_end_date}]


@freeze_time("2021-11-30")
def test_empty_stream_slice_if_abnormal_state_is_passed(test_config, mock_metrics_dimensions_type_list_link):
    g = GoogleAnalyticsV4IncrementalObjectsBase(config=test_config)
    stream_state = {"ga_date": "2050-05-01"}
    slices = g.stream_slices(stream_state=stream_state)
    assert slices == [None]


def test_empty_slice_produces_no_records(test_config, mock_metrics_dimensions_type_list_link):
    g = GoogleAnalyticsV4IncrementalObjectsBase(config=test_config)
    records = g.read_records(sync_mode=SyncMode.incremental, stream_slice=None, stream_state={g.cursor_field: g.start_date})
    assert next(iter(records), None) is None


def test_state_saved_after_each_record(test_config, mock_metrics_dimensions_type_list_link):
    today_dt = pendulum.now().date()
    before_yesterday = today_dt.subtract(days=2).strftime("%Y-%m-%d")
    today = today_dt.strftime("%Y-%m-%d")
    record = {"ga_date": today}
    g = GoogleAnalyticsV4IncrementalObjectsBase(config=test_config)
    state = {g.cursor_field: before_yesterday}
    assert g.get_updated_state(state, record) == {g.cursor_field: today}


def test_connection_fail_invalid_reports_json(test_config):
    source = SourceGoogleAnalyticsV4()
    test_config["custom_reports"] = "[{'data': {'ga:foo': 'ga:bar'}}]"
    ok, error = source.check_connection(logging.getLogger(), test_config)
    assert not ok
    assert "Invalid custom reports json structure." in error


@pytest.mark.parametrize(
    ("status", "json_resp"),
    (
        (403, {"error": "Your role is not not granted the permission for accessing this resource"}),
        (500, {"error": "Internal server error, please contact support"}),
    ),
)
def test_connection_fail_due_to_http_status(
    mocker, test_config, requests_mock, mock_auth_call, mock_metrics_dimensions_type_list_link, status, json_resp
):
    mocker.patch("time.sleep")
    requests_mock.post("https://analyticsreporting.googleapis.com/v4/reports:batchGet", status_code=status, json=json_resp)
    source = SourceGoogleAnalyticsV4()
    ok, error = source.check_connection(logging.getLogger(), test_config)
    assert not ok
    if status == 403:
        assert "Please check the permissions for the requested view_id" in error
        assert test_config["view_id"] in error
    assert json_resp["error"] in error


def test_is_data_golden_flag_missing_equals_false(
    mock_api_returns_is_data_golden_false, test_config, configured_catalog, mock_metrics_dimensions_type_list_link, mock_auth_call
):
    source = SourceGoogleAnalyticsV4()
    for message in source.read(logging.getLogger(), test_config, configured_catalog):
        if message.type == Type.RECORD:
            assert message.record.data["isDataGolden"] is False
