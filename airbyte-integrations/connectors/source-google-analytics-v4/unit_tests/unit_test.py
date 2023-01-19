#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from unittest.mock import MagicMock, patch
from urllib.parse import unquote

import pendulum
import pytest
from airbyte_cdk.models import SyncMode, Type
from freezegun import freeze_time
from source_google_analytics_v4.source import (
    DATA_IS_NOT_GOLDEN_MSG,
    RESULT_IS_SAMPLED_MSG,
    GoogleAnalyticsV4IncrementalObjectsBase,
    GoogleAnalyticsV4Stream,
    GoogleAnalyticsV4TypesList,
    SourceGoogleAnalyticsV4,
)

expected_metrics_dimensions_type_map = (
    {"ga:users": "INTEGER", "ga:newUsers": "INTEGER"},
    {"ga:date": "STRING", "ga:country": "STRING"},
)


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
    requests_mock,
    mock_metrics_dimensions_type_list_link,
    mock_auth_call
):
    """
    check_connection fails because of the API returns no records,
    then we assume than user doesn't have permission to read requested `view`
    """
    source = SourceGoogleAnalyticsV4()
    requests_mock.register_uri("POST", "https://analyticsreporting.googleapis.com/v4/reports:batchGet",
                               [{"status_code": 403,
                                 "json": {"results": [],
                                          "error": "User does not have sufficient permissions for this profile."}}])

    is_success, msg = source.check_connection(MagicMock(), test_config_auth_service)
    assert is_success is False
    assert (
        msg
        == f"Please check the permissions for the requested view_id: {test_config_auth_service['view_id']}. "
           f"User does not have sufficient permissions for this profile."
    )
    jwt_encode_mock.encode.assert_called()
    assert mock_auth_call.called


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
    mock_metrics_dimensions_type_list_link,
    mock_auth_call,
    requests_mock
):
    """
    check_connection fails because of the API returns no records,
    then we assume than user doesn't have permission to read requested `view`
    """
    source = SourceGoogleAnalyticsV4()
    requests_mock.register_uri("POST", "https://analyticsreporting.googleapis.com/v4/reports:batchGet",
                               [{"status_code": 403,
                                 "json": {"results": [],
                                          "error": "User does not have sufficient permissions for this profile."}}])
    is_success, msg = source.check_connection(MagicMock(), test_config)
    assert is_success is False
    assert (
        msg == f"Please check the permissions for the requested view_id: {test_config['view_id']}."
               f" User does not have sufficient permissions for this profile."
    )
    jwt_encode_mock.encode.assert_not_called()
    assert "https://www.googleapis.com/auth/analytics.readonly" in unquote(mock_auth_call.last_request.body)
    assert "client_id_val" in unquote(mock_auth_call.last_request.body)
    assert "client_secret_val" in unquote(mock_auth_call.last_request.body)
    assert "refresh_token_val" in unquote(mock_auth_call.last_request.body)
    assert mock_auth_call.called


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


def test_unknown_metrics_or_dimensions_error_validation(
    mocker, test_config, mock_metrics_dimensions_type_list_link, mock_unknown_metrics_or_dimensions_error
):
    records = GoogleAnalyticsV4Stream(test_config).read_records(sync_mode=None)
    assert list(records) == []


def test_daily_request_limit_error_validation(mocker, test_config, mock_metrics_dimensions_type_list_link, mock_daily_request_limit_error):
    records = GoogleAnalyticsV4Stream(test_config).read_records(sync_mode=None)
    assert list(records) == []


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
    test_config["custom_reports"] = '[{{"name": "test", "dimensions": [], "metrics": []}}]'
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


@pytest.mark.parametrize(
    "configured_response, expected_token",
    (
        ({}, None),
        ({"reports": []}, None),
        ({"reports": [{"data": {}, "columnHeader": {}}]}, None),
        ({"reports": [{"data": {}, "columnHeader": {}, "nextPageToken": 100000}]}, {"pageToken": 100000}),
    ),
)
def test_next_page_token(test_config, configured_response, expected_token):
    response = MagicMock(json=MagicMock(return_value=configured_response))
    token = GoogleAnalyticsV4Stream(test_config).next_page_token(response)
    assert token == expected_token
