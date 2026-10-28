#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock

import pytest
import requests
import yaml

from airbyte_cdk.models import ConnectorSpecification, FailureType, Status, SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read

from .conftest import _YAML_FILE_PATH, get_source


_PRODUCTION_ONLY_STREAMS = {
    "advertiser_ids",
    "ads_reports_by_country_daily",
    "ad_groups_reports_by_country_daily",
    "advertisers_reports_daily",
    "advertisers_audience_reports_daily",
    "advertisers_audience_reports_by_country_daily",
    "advertisers_audience_reports_by_platform_daily",
    "ads_reports_by_country_hourly",
    "advertisers_reports_hourly",
    "ad_groups_reports_by_country_hourly",
    "advertisers_reports_lifetime",
    "advertisers_audience_reports_lifetime",
    "spark_ads",
    "pixels",
    "pixel_instant_page_events",
    "pixel_events_statistics",
}
_COMMON_STREAMS = {"advertisers", "ads", "ad_groups", "campaigns"}


def _walk_response_filters(value):
    if isinstance(value, dict):
        if isinstance(value.get("response_filters"), list):
            yield value["response_filters"]
        for child in value.values():
            yield from _walk_response_filters(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_response_filters(child)


@pytest.mark.parametrize(
    "config, stream_len",
    [
        ({"access_token": "token", "environment": {"app_id": "1111", "secret": "secret"}, "start_date": "2021-04-01"}, 44),
        ({"access_token": "token", "environment": {"app_id": "1111", "secret": ""}, "start_date": "2021-04-01"}, 28),
        ({"access_token": "token", "start_date": "2021-01-01", "environment": {"advertiser_id": "1111"}}, 28),
        (
            {
                "access_token": "token",
                "environment": {"app_id": "1111", "secret": "secret"},
                "start_date": "2021-04-01",
                "report_granularity": "LIFETIME",
            },
            44,
        ),
        (
            {
                "access_token": "token",
                "environment": {"app_id": "1111", "secret": "secret"},
                "start_date": "2021-04-01",
                "report_granularity": "DAY",
            },
            44,
        ),
    ],
)
def test_source_streams(config, stream_len):
    streams = get_source(config=config, state=None).streams(config=config)
    assert len(streams) == stream_len


@pytest.mark.parametrize(
    "config, expects_production_streams",
    [
        (
            {"access_token": "token", "start_date": "2021-04-01", "environment": {"app_id": "1111", "secret": ""}},
            False,
        ),
        (
            {"access_token": "token", "start_date": "2021-04-01", "environment": {"app_id": "1111", "secret": None}},
            False,
        ),
        ({"access_token": "token", "start_date": "2021-04-01", "environment": {"app_id": "1111"}}, False),
        (
            {"access_token": "token", "start_date": "2021-04-01", "environment": {"app_id": "1111", "secret": "secret"}},
            True,
        ),
        (
            {
                "access_token": "token",
                "start_date": "2021-04-01",
                "credentials": {"auth_type": "sandbox_access_token", "advertiser_id": "1111", "access_token": "token"},
            },
            False,
        ),
        (
            {
                "access_token": "token",
                "start_date": "2021-04-01",
                "credentials": {
                    "auth_type": "oauth2.0",
                    "app_id": "1111",
                    "secret": "secret",
                    "access_token": "token",
                },
            },
            True,
        ),
    ],
)
def test_conditional_production_streams(config, expects_production_streams):
    names = {stream.name for stream in get_source(config=config, state=None).streams(config=config)}
    production_set = _PRODUCTION_ONLY_STREAMS

    if expects_production_streams:
        assert production_set <= names
    else:
        assert production_set.isdisjoint(names)
    assert _COMMON_STREAMS <= names


def test_source_spec(config):
    spec = get_source(config=config, state=None).spec(logger=None)
    assert isinstance(spec, ConnectorSpecification)


def test_51004_retry_handlers_also_retry_51002():
    with _YAML_FILE_PATH.open() as manifest_file:
        manifest = yaml.safe_load(manifest_file)

    for response_filters in _walk_response_filters(manifest):
        retries_51004 = any(
            "response.get('code') == 51004" in response_filter.get("predicate", "") and response_filter.get("action") == "RETRY"
            for response_filter in response_filters
        )
        if retries_51004:
            assert any(
                "response.get('code') == 51002" in response_filter.get("predicate", "") and response_filter.get("action") == "RETRY"
                for response_filter in response_filters
            )


def test_every_40067_filter_splits_the_request_window(config):
    filters_40067 = [
        response_filter
        for response_filters in _walk_response_filters(get_source(config=config, state=None).resolved_manifest)
        for response_filter in response_filters
        if "40067" in response_filter.get("predicate", "")
    ]
    assert filters_40067
    assert all(
        response_filter.get("action") == "SPLIT_REQUEST_WINDOW" for response_filter in filters_40067
    ), "Error 40067 must split the request window instead of failing"


@pytest.fixture(name="config")
def config_fixture():
    config = {
        "account_id": 123,
        "access_token": "TOKEN",
        "start_date": "2019-10-10T00:00:00",
        "end_date": "2020-10-10T00:00:00",
    }
    return config


def test_source_check_connection_ok(config, requests_mock):
    requests_mock.get(
        "https://business-api.tiktok.com/open_api/v1.3/oauth2/advertiser/get/",
        json={
            "code": 0,
            "message": "ok",
            "data": {
                "list": [
                    {"advertiser_id": "917429327", "advertiser_name": "name"},
                ]
            },
        },
    )
    requests_mock.get(
        "https://business-api.tiktok.com/open_api/v1.3/advertiser/info/?page_size=100&advertiser_ids=%5B%22917429327%22%5D",
        json={
            "code": 0,
            "message": "ok",
            "data": {
                "list": [
                    {"advertiser_id": "917429327", "advertiser_name": "name"},
                ]
            },
        },
    )
    logger_mock = MagicMock()
    assert get_source(config=config, state=None).check(logger_mock, config).status == Status.SUCCEEDED


@pytest.mark.parametrize(
    "json_response, expected_result, expected_message",
    [
        (
            {"code": 40105, "message": "Access token is incorrect or has been revoked."},
            (
                Status.FAILED,
                "Stream advertisers is not available: TikTok Marketing API returned an error (code 40105): Access token is incorrect or has been revoked.",
            ),
            None,
        ),
        ({"code": 40100, "message": "App reaches the QPS limit."}, None, 10),
        (
            {"code": 40001, "message": "Permission error: The access token lacks the required scope for endpoint."},
            (Status.FAILED, "Insufficient permissions for this endpoint (error 40001)"),
            None,
        ),
    ],
)
@pytest.mark.usefixtures("mock_sleep")
def test_source_check_connection_failed(config, requests_mock, capsys, json_response, expected_result, expected_message):
    requests_mock.get("https://business-api.tiktok.com/open_api/v1.3/oauth2/advertiser/get/", json=json_response)
    requests_mock.get(
        "https://business-api.tiktok.com/open_api/v1.3/advertiser/info/?page_size=100&advertiser_ids=%5B%22917429327%22%5D",
        json=json_response,
    )

    logger_mock = MagicMock()
    result = get_source(config=config, state=None).check(logger_mock, config)

    if expected_result is not None:
        assert result.status == expected_result[0]
        assert expected_result[1] in result.message
    if expected_message is not None:
        trace_messages = capsys.readouterr().out.split()
        assert len(trace_messages) == expected_message


def test_error_40001_classified_as_config_error(requests_mock):
    """Error code 40001 (PERMISSION_ERROR) must be classified as config_error, not system_error."""
    config = {"access_token": "TOKEN", "start_date": "2024-01-01", "end_date": "2024-01-02"}
    json_response = {"code": 40001, "message": "Permission error: The access token lacks the required scope."}
    ok_response = {"code": 0, "message": "ok", "data": {"list": [{"advertiser_id": "917429327", "advertiser_name": "name"}]}}

    requests_mock.get("https://business-api.tiktok.com/open_api/v1.3/oauth2/advertiser/get/", json=ok_response)
    requests_mock.get("https://business-api.tiktok.com/open_api/v1.3/advertiser/info/", json=ok_response)
    report_mock = requests_mock.get("https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/", json=json_response)

    catalog = CatalogBuilder().with_stream("ads_reports_daily", SyncMode.full_refresh).build()
    source = get_source(config=config, state=None)
    output = read(source, config, catalog)

    assert report_mock.called, "Expected the report endpoint to be requested"
    assert len(output.errors) > 0, "Expected at least one error trace for 40001"
    for error_msg in output.errors:
        assert (
            error_msg.trace.error.failure_type == FailureType.config_error
        ), f"Error 40001 should be config_error but got {error_msg.trace.error.failure_type}"
    assert any("Insufficient permissions for this endpoint (error 40001)" in error_msg.trace.error.message for error_msg in output.errors)


def _catch_all_fail_filters(manifest):
    return [
        response_filter
        for response_filters in _walk_response_filters(manifest)
        for response_filter in response_filters
        if response_filter.get("predicate") == "{{ response.get('code') != 0 }}" and response_filter.get("action") == "FAIL"
    ]


def test_every_catch_all_fail_filter_includes_tiktok_error_code(config):
    from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString

    catch_all_filters = _catch_all_fail_filters(get_source(config=config, state=None).resolved_manifest)
    assert catch_all_filters

    for response_filter in catch_all_filters:
        assert "failure_type" not in response_filter, "Catch-all filter must keep the default system_error failure type"
        error_message = InterpolatedString.create(response_filter["error_message"], parameters={})
        rendered = error_message.eval(config, response={"code": 51001, "message": "internal service timeout"})
        assert rendered == "TikTok Marketing API returned an error (code 51001): internal service timeout"
        assert error_message.eval(config, response={"code": 51001}) == "TikTok Marketing API returned an error (code 51001): "


def test_unhandled_error_code_surfaces_tiktok_code_in_message(requests_mock):
    config = {"access_token": "TOKEN", "start_date": "2024-01-01", "end_date": "2024-01-02"}
    error_response = {"code": 59999, "message": "internal service timeout", "request_id": "abc", "data": {}}
    ok_response = {"code": 0, "message": "ok", "data": {"list": [{"advertiser_id": "917429327", "advertiser_name": "name"}]}}

    requests_mock.get("https://business-api.tiktok.com/open_api/v1.3/oauth2/advertiser/get/", json=ok_response)
    requests_mock.get("https://business-api.tiktok.com/open_api/v1.3/advertiser/info/", json=ok_response)
    report_mock = requests_mock.get("https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/", json=error_response)

    catalog = CatalogBuilder().with_stream("ads_reports_daily", SyncMode.full_refresh).build()
    output = read(get_source(config=config, state=None), config, catalog)

    assert report_mock.called, "Expected the report endpoint to be requested"
    stream_errors = [
        error_msg
        for error_msg in output.errors
        if error_msg.trace.error.message == "TikTok Marketing API returned an error (code 59999): internal service timeout"
    ]
    assert stream_errors, f"Expected the TikTok error code in the message, got {[e.trace.error.message for e in output.errors]}"
    assert all(error_msg.trace.error.failure_type == FailureType.system_error for error_msg in stream_errors)


def _walk_error_handlers(value):
    if isinstance(value, dict):
        if value.get("type") == "DefaultErrorHandler" and isinstance(value.get("response_filters"), list):
            yield value
        for child in value.values():
            yield from _walk_error_handlers(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_error_handlers(child)


@pytest.mark.parametrize("code", [51001, 51043])
def test_internal_service_timeout_codes_are_retried(config, code):
    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps({"code": code, "message": "internal service timeout", "request_id": "1"}).encode()
    factory = ModelToComponentFactory()

    error_handlers = list(_walk_error_handlers(get_source(config=config, state=None).resolved_manifest))
    assert error_handlers
    for error_handler_definition in error_handlers:
        error_handler_definition = {
            **error_handler_definition,
            "response_filters": [
                {"type": "HttpResponseFilter", **response_filter} for response_filter in error_handler_definition["response_filters"]
            ],
        }
        error_handler = factory.create_component(DefaultErrorHandlerModel, error_handler_definition, config)
        resolution = error_handler.interpret_response(response)
        assert resolution.response_action == ResponseAction.RETRY
        assert f"code {code}" in resolution.error_message
        assert "transient" in resolution.error_message
