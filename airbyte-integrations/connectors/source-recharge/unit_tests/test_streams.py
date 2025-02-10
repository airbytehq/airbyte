#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from http import HTTPStatus
from typing import Any, List, Mapping, MutableMapping, Union

import pytest
import requests
from source_recharge.source import Orders, RechargeTokenAuthenticator, SourceRecharge

from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


def use_orders_deprecated_api_config(
    config: Mapping[str, Any] = None,
    use_deprecated_api: bool = False,
) -> MutableMapping[str, Any]:
    test_config = config
    if use_deprecated_api:
        test_config["use_orders_deprecated_api"] = use_deprecated_api
    return test_config


def test_get_auth_header(config) -> None:
    expected = {"X-Recharge-Access-Token": config.get("access_token")}
    actual = RechargeTokenAuthenticator(token=config["access_token"]).get_auth_header()
    assert actual == expected


def test_streams(config) -> None:
    streams = SourceRecharge().streams(config)
    assert len(streams) == 13


class TestCommon:
    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Orders, "id"),
        ],
    )
    def test_primary_key(self, stream_cls, expected) -> None:
        assert expected == stream_cls.primary_key

    @pytest.mark.parametrize(
        "stream_cls, stream_type, expected",
        [
            (Orders, "incremental", "orders"),
        ],
    )
    def test_data_path(self, config, stream_cls, stream_type, expected) -> None:
        if stream_type == "incremental":
            result = stream_cls(config, authenticator=None).data_path
        else:
            result = stream_cls(config, authenticator=None).data_path
        assert expected == result

    @pytest.mark.parametrize(
        "stream_cls, stream_type, expected",
        [
            (Orders, "incremental", "orders"),
        ],
    )
    def test_path(self, config, stream_cls, stream_type, expected) -> None:
        if stream_type == "incremental":
            result = stream_cls(config, authenticator=None).path()
        else:
            result = stream_cls(config, authenticator=None).path()
        assert expected == result

    @pytest.mark.parametrize(
        ("http_status", "headers", "expected_action"),
        [
            (HTTPStatus.OK, {"Content-Length": 256}, ResponseAction.RETRY),
            (HTTPStatus.BAD_REQUEST, {}, ResponseAction.FAIL),
            (HTTPStatus.TOO_MANY_REQUESTS, {}, ResponseAction.RATE_LIMITED),
            (HTTPStatus.INTERNAL_SERVER_ERROR, {}, ResponseAction.RETRY),
            (HTTPStatus.FORBIDDEN, {}, ResponseAction.FAIL),
        ],
    )
    def test_should_retry(self, config, http_status, headers, expected_action) -> None:
        response = requests.Response()
        response.status_code = http_status
        response._content = b""
        response.headers = headers
        stream = Orders(config, authenticator=None)
        error_resolution = stream.get_error_handler().interpret_response(response)
        error_resolution.response_action == expected_action


class TestFullRefreshStreams:
    def generate_records(self, stream_name, count) -> Union[Mapping[str, List[Mapping[str, Any]]], Mapping[str, Any]]:
        if not stream_name:
            return {f"record_{1}": f"test_{1}"}
        result = []
        for i in range(0, count):
            result.append({f"record_{i}": f"test_{i}"})
        return {stream_name: result}

    @pytest.mark.parametrize(
        "stream_cls, use_deprecated_api, cursor_response, expected",
        [
            (Orders, True, {}, {"page": 2}),
            (Orders, False, {"next_cursor": "some next cursor"}, {"cursor": "some next cursor"}),
        ],
    )
    def test_next_page_token(self, config, use_deprecated_api, stream_cls, cursor_response, requests_mock, expected) -> None:
        test_config = use_orders_deprecated_api_config(config, use_deprecated_api)
        stream = stream_cls(test_config, authenticator=None)
        stream.page_size = 2
        url = f"{stream.url_base}{stream.path()}"
        response = {**cursor_response, **self.generate_records(stream.data_path, 2)}
        requests_mock.get(url, json=response)
        response = requests.get(url)
        assert stream.next_page_token(response) == expected

    @pytest.mark.parametrize(
        "stream_cls, use_deprecated_api, next_page_token, stream_slice, expected",
        [
            (
                Orders,
                True,
                None,
                {"start_date": "2023-01-01 00:00:01", "end_date": "2023-01-31 00:00:01"},
                {
                    "limit": 250,
                    "sort_by": "updated_at-asc",
                    "updated_at_min": "2023-01-01 00:00:01",
                    "updated_at_max": "2023-01-31 00:00:01",
                },
            ),
            (
                Orders,
                False,
                None,
                {"start_date": "2023-01-01 00:00:01", "end_date": "2023-01-31 00:00:01"},
                {
                    "limit": 250,
                    "sort_by": "updated_at-asc",
                    "updated_at_min": "2023-01-01 00:00:01",
                    "updated_at_max": "2023-01-31 00:00:01",
                },
            ),
        ],
    )
    def test_request_params(self, config, stream_cls, use_deprecated_api, next_page_token, stream_slice, expected) -> None:
        test_config = use_orders_deprecated_api_config(config, use_deprecated_api)
        stream = stream_cls(test_config, authenticator=None)
        result = stream.request_params(stream_slice, next_page_token)
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, use_deprecated_api, data, expected",
        [
            (Orders, True, [{"test": 123}], [{"test": 123}]),
            (Orders, False, [{"test": 123}], [{"test": 123}]),
        ],
    )
    def test_parse_response(self, config, stream_cls, use_deprecated_api, data, requests_mock, expected) -> None:
        test_config = use_orders_deprecated_api_config(config, use_deprecated_api)
        stream = stream_cls(test_config, authenticator=None)
        url = f"{stream.url_base}{stream.path()}"
        data = {stream.data_path: data} if stream.data_path else data
        requests_mock.get(url, json=data)
        response = requests.get(url)
        assert list(stream.parse_response(response)) == expected

    @pytest.mark.parametrize(
        "stream_cls, use_deprecated_api, data, expected",
        [
            (Orders, True, [{"test": 123}], [{"test": 123}]),
            (Orders, False, [{"test": 123}], [{"test": 123}]),
        ],
    )
    def get_stream_data(self, config, stream_cls, use_deprecated_api, data, requests_mock, expected) -> None:
        test_config = use_orders_deprecated_api_config(config, use_deprecated_api)
        stream = stream_cls(test_config, authenticator=None)
        url = f"{stream.url_base}{stream.path()}"
        data = {stream.data_path: data} if stream.data_path else data
        requests_mock.get(url, json=data)
        response = requests.get(url)
        assert list(stream.parse_response(response)) == expected


class TestIncrementalStreams:
    def generate_records(self, stream_name, count) -> Mapping[str, List[Mapping[str, Any]]]:
        result = []
        for i in range(0, count):
            result.append({f"record_{i}": f"test_{i}"})
        return {stream_name: result}

    @pytest.mark.parametrize(
        "stream_cls, use_deprecated_api, expected",
        [
            (Orders, True, "updated_at"),
            (Orders, False, "updated_at"),
        ],
    )
    def test_cursor_field(self, config, stream_cls, use_deprecated_api, expected) -> None:
        test_config = use_orders_deprecated_api_config(config, use_deprecated_api)
        stream = stream_cls(test_config, authenticator=None)
        result = stream.cursor_field
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, use_deprecated_api, cursor_response, expected",
        [
            (Orders, True, {}, {"page": 2}),
            (Orders, False, {"next_cursor": "some next cursor"}, {"cursor": "some next cursor"}),
        ],
    )
    def test_next_page_token(self, config, stream_cls, use_deprecated_api, cursor_response, requests_mock, expected) -> None:
        test_config = use_orders_deprecated_api_config(config, use_deprecated_api)
        stream = stream_cls(test_config, authenticator=None)
        stream.page_size = 2
        url = f"{stream.url_base}{stream.path()}"
        response = {**cursor_response, **self.generate_records(stream.data_path, 2)}
        requests_mock.get(url, json=response)
        response = requests.get(url)
        assert stream.next_page_token(response) == expected

    @pytest.mark.parametrize(
        "stream_cls, use_deprecated_api, next_page_token, stream_slice, expected",
        [
            (
                Orders,
                True,
                None,
                {"start_date": "2020-01-01T00:00:00Z", "end_date": "2020-02-01T00:00:00Z"},
                {
                    "limit": 250,
                    "sort_by": "updated_at-asc",
                    "updated_at_min": "2020-01-01T00:00:00Z",
                    "updated_at_max": "2020-02-01T00:00:00Z",
                },
            ),
            (
                Orders,
                False,
                None,
                {"start_date": "2020-01-01T00:00:00Z", "end_date": "2020-02-01T00:00:00Z"},
                {
                    "limit": 250,
                    "sort_by": "updated_at-asc",
                    "updated_at_min": "2020-01-01T00:00:00Z",
                    "updated_at_max": "2020-02-01T00:00:00Z",
                },
            ),
        ],
    )
    def test_request_params(self, config, stream_cls, use_deprecated_api, next_page_token, stream_slice, expected) -> None:
        test_config = use_orders_deprecated_api_config(config, use_deprecated_api)
        stream = stream_cls(test_config, authenticator=None)
        result = stream.request_params(stream_slice, next_page_token)
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, use_deprecated_api, current_state, latest_record, expected",
        [
            (Orders, True, {"updated_at": 5}, {"updated_at": 5}, {"updated_at": 5}),
            (Orders, False, {"updated_at": 5}, {"updated_at": 5}, {"updated_at": 5}),
        ],
    )
    def test_get_updated_state(self, config, stream_cls, use_deprecated_api, current_state, latest_record, expected) -> None:
        test_config = use_orders_deprecated_api_config(config, use_deprecated_api)
        stream = stream_cls(test_config, authenticator=None)
        result = stream.get_updated_state(current_state, latest_record)
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Orders, {"start_date": "2021-08-15 00:00:01", "end_date": "2021-09-14 00:00:01"}),
        ],
    )
    def test_stream_slices(self, config, stream_cls, expected) -> None:
        stream = stream_cls(config, authenticator=None)
        result = list(stream.stream_slices(sync_mode=None, cursor_field=stream.cursor_field, stream_state=None))
        assert result[0] == expected
