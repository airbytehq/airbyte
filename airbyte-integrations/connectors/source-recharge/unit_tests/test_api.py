#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import patch

import pytest
import requests
from source_recharge.api import (
    Addresses,
    Charges,
    Collections,
    Customers,
    Discounts,
    Metafields,
    Onetimes,
    Orders,
    Products,
    RechargeStream,
    Shop,
    Subscriptions,
)


# config
@pytest.fixture(name="config")
def config():
    return {
        "authenticator": None,
        "access_token": "access_token",
        "start_date": "2021-08-15T00:00:00Z",
    }


class TestCommon:
    main = RechargeStream

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Addresses, "id"),
            (Charges, "id"),
            (Collections, "id"),
            (Customers, "id"),
            (Discounts, "id"),
            (Metafields, "id"),
            (Onetimes, "id"),
            (Orders, "id"),
            (Products, "id"),
            (Shop, ["shop", "store"]),
            (Subscriptions, "id"),
        ],
    )
    def test_primary_key(self, stream_cls, expected):
        assert expected == stream_cls.primary_key

    @pytest.mark.parametrize(
        "stream_cls",
        [
            (Addresses),
            (Charges),
            (Collections),
            (Customers),
            (Discounts),
            (Metafields),
            (Onetimes),
            (Orders),
            (Products),
            (Shop),
            (Subscriptions),
        ],
    )
    def test_url_base(self, config, stream_cls):
        expected = self.main(config, authenticator=None).url_base
        result = stream_cls.url_base
        assert expected == result

    @pytest.mark.parametrize(
        "stream_cls",
        [
            (Addresses),
            (Charges),
            (Collections),
            (Customers),
            (Discounts),
            (Metafields),
            (Onetimes),
            (Orders),
            (Products),
            (Shop),
            (Subscriptions),
        ],
    )
    def test_limit(self, config, stream_cls):
        expected = self.main(config, authenticator=None).limit
        result = stream_cls.limit
        assert expected == result

    @pytest.mark.parametrize(
        "stream_cls",
        [
            (Addresses),
            (Charges),
            (Collections),
            (Customers),
            (Discounts),
            (Metafields),
            (Onetimes),
            (Orders),
            (Products),
            (Shop),
            (Subscriptions),
        ],
    )
    def test_page_num(self, config, stream_cls):
        expected = self.main(config, authenticator=None).page_num
        result = stream_cls.page_num
        assert expected == result

    @pytest.mark.parametrize(
        "stream_cls, stream_type, expected",
        [
            (Addresses, "incremental", "addresses"),
            (Charges, "incremental", "charges"),
            (Collections, "full-refresh", "collections"),
            (Customers, "incremental", "customers"),
            (Discounts, "incremental", "discounts"),
            (Metafields, "full-refresh", "metafields"),
            (Onetimes, "incremental", "onetimes"),
            (Orders, "incremental", "orders"),
            (Products, "full-refresh", "products"),
            (Shop, "full-refresh", None),
            (Subscriptions, "incremental", "subscriptions"),
        ],
    )
    def test_data_path(self, config, stream_cls, stream_type, expected):
        if stream_type == "incremental":
            result = stream_cls(config, authenticator=None).data_path
        else:
            result = stream_cls(config, authenticator=None).data_path
        assert expected == result

    @pytest.mark.parametrize(
        "stream_cls, stream_type, expected",
        [
            (Addresses, "incremental", "addresses"),
            (Charges, "incremental", "charges"),
            (Collections, "full-refresh", "collections"),
            (Customers, "incremental", "customers"),
            (Discounts, "incremental", "discounts"),
            (Metafields, "full-refresh", "metafields"),
            (Onetimes, "incremental", "onetimes"),
            (Orders, "incremental", "orders"),
            (Products, "full-refresh", "products"),
            (Shop, "full-refresh", "shop"),
            (Subscriptions, "incremental", "subscriptions"),
        ],
    )
    def test_path(self, config, stream_cls, stream_type, expected):
        if stream_type == "incremental":
            result = stream_cls(config, authenticator=None).path()
        else:
            result = stream_cls(config, authenticator=None).path()
        assert expected == result

    @pytest.mark.parametrize(
        ("http_status", "headers", "should_retry"),
        [
            (HTTPStatus.OK, {"Content-Length": 256}, True),
            (HTTPStatus.BAD_REQUEST, {}, False),
            (HTTPStatus.TOO_MANY_REQUESTS, {}, True),
            (HTTPStatus.INTERNAL_SERVER_ERROR, {}, True),
            (HTTPStatus.FORBIDDEN, {}, False),
        ],
    )
    def test_should_retry(self, config, http_status, headers, should_retry):
        response = requests.Response()
        response.status_code = http_status
        response._content = b""
        response.headers = headers
        stream = RechargeStream(config, authenticator=None)
        assert stream.should_retry(response) == should_retry


class TestFullRefreshStreams:
    def generate_records(self, stream_name, count):
        result = []
        for i in range(0, count):
            result.append({f"record_{i}": f"test_{i}"})
        return {stream_name: result}

    @pytest.mark.parametrize(
        "stream_cls, cursor_response, expected",
        [
            (Collections, "some next cursor", {"cursor": "some next cursor"}),
            (Metafields, "some next cursor", {"cursor": "some next cursor"}),
            (Products, "some next cursor", {"cursor": "some next cursor"}),
            (Shop, "some next cursor", {"cursor": "some next cursor"}),
        ],
    )
    def test_next_page_token(self, config, stream_cls, cursor_response, requests_mock, expected):
        stream = stream_cls(config, authenticator=None)
        stream.limit = 2
        url = f"{stream.url_base}{stream.path()}"
        response = {"next_cursor": cursor_response, stream.name: self.generate_records(stream.name, 2)}
        requests_mock.get(url, json=response)
        response = requests.get(url)
        assert stream.next_page_token(response) == expected

    @pytest.mark.parametrize(
        "stream_cls, next_page_token, stream_state, stream_slice, expected",
        [
            (Collections, None, {}, {}, {"limit": 250, "updated_at_min": "2021-08-15T00:00:00Z"}),
            (Metafields, {"cursor": "12353"}, {"updated_at": "2030-01-01"}, {}, {"limit": 250, "owner_resource": None, "cursor": "12353"}),
            (Products, None, {}, {}, {"limit": 250, "updated_at_min": "2021-08-15T00:00:00Z"}),
            (Shop, None, {}, {}, {"limit": 250, "updated_at_min": "2021-08-15T00:00:00Z",}),
        ],
    )
    def test_request_params(self, config, stream_cls, next_page_token, stream_state, stream_slice, expected):
        stream = stream_cls(config, authenticator=None)
        result = stream.request_params(stream_state, stream_slice, next_page_token)
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, data, expected",
        [
            (Collections, [{"test": 123}], [{"test": 123}]),
            (Metafields, [{"test2": 234}], [{"test2": 234}]),
            (Products, [{"test3": 345}], [{"test3": 345}]),
            (Shop, {"test4": 456}, [{"test4": 456}]),
        ],
    )
    def test_parse_response(self, config, stream_cls, data, requests_mock, expected):
        stream = stream_cls(config, authenticator=None)
        url = f"{stream.url_base}{stream.path()}"
        data = {stream.data_path: data} if stream.data_path else data
        requests_mock.get(url, json=data)
        response = requests.get(url)
        assert list(stream.parse_response(response)) == expected

    @pytest.mark.parametrize(
        "stream_cls, data, expected",
        [
            (Collections, [{"test": 123}], [{"test": 123}]),
            (Metafields, [{"test2": 234}], [{"test2": 234}]),
            (Products, [{"test3": 345}], [{"test3": 345}]),
            (Shop, {"test4": 456}, [{"test4": 456}]),
        ],
    )
    def get_stream_data(self, config, stream_cls, data, requests_mock, expected):
        stream = stream_cls(config, authenticator=None)
        url = f"{stream.url_base}{stream.path()}"
        data = {stream.data_path: data} if stream.data_path else data
        requests_mock.get(url, json=data)
        response = requests.get(url)
        assert list(stream.parse_response(response)) == expected

    @pytest.mark.parametrize("owner_resource, expected", [({"customer": {"id": 123}}, {"customer": {"id": 123}})])
    def test_metafields_read_records(self, config, owner_resource, expected):
        with patch.object(Metafields, "read_records", return_value=owner_resource):
            result = Metafields(config).read_records(stream_slice={"owner_resource": owner_resource})
            assert result == expected


class TestIncrementalStreams:
    def generate_records(self, stream_name, count):
        result = []
        for i in range(0, count):
            result.append({f"record_{i}": f"test_{i}"})
        return {stream_name: result}

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Addresses, "updated_at"),
            (Charges, "updated_at"),
            (Customers, "updated_at"),
            (Discounts, "updated_at"),
            (Onetimes, "updated_at"),
            (Orders, "updated_at"),
            (Subscriptions, "updated_at"),
        ],
    )
    def test_cursor_field(self, config, stream_cls, expected):
        stream = stream_cls(config, authenticator=None)
        result = stream.cursor_field
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, cursor_response, expected",
        [
            (Addresses, "some next cursor", {"cursor": "some next cursor"}),
            (Charges, "some next cursor", {"cursor": "some next cursor"}),
            (Customers, "some next cursor", {"cursor": "some next cursor"}),
            (Discounts, "some next cursor", {"cursor": "some next cursor"}),
            (Onetimes, "some next cursor", {"cursor": "some next cursor"}),
            (Orders, "some next cursor", {"cursor": "some next cursor"}),
            (Subscriptions, "some next cursor", {"cursor": "some next cursor"}),
        ],
    )
    def test_next_page_token(self, config, stream_cls, cursor_response, requests_mock, expected):
        stream = stream_cls(config, authenticator=None)
        stream.limit = 2
        url = f"{stream.url_base}{stream.path()}"
        response = {"next_cursor": cursor_response, stream.name: self.generate_records(stream.name, 2)}
        requests_mock.get(url, json=response)
        response = requests.get(url)
        assert stream.next_page_token(response) == expected

    @pytest.mark.parametrize(
        "stream_cls, next_page_token, stream_state, stream_slice, expected",
        [
            (Addresses, None, {}, {}, {"limit": 250, "updated_at_min": "2021-08-15T00:00:00Z"}),
            (Charges, {"cursor": "123"}, {"updated_at": "2030-01-01"}, {},
             {"limit": 250, "cursor": "123"}),
            (Customers, None, {}, {}, {"limit": 250, "updated_at_min": "2021-08-15T00:00:00Z"}),
            (Discounts, None, {}, {}, {"limit": 250, "updated_at_min": "2021-08-15T00:00:00Z"}),
            (Onetimes, {"cursor": "123"}, {"updated_at": "2030-01-01"}, {},
             {"limit": 250, "cursor": "123"}),
            (Orders, None, {}, {}, {"limit": 250, "updated_at_min": "2021-08-15T00:00:00Z"}),
            (Subscriptions, None, {}, {},
             {"limit": 250, "updated_at_min": "2021-08-15T00:00:00Z"}),
        ],
    )
    def test_request_params(self, config, stream_cls, next_page_token, stream_state, stream_slice, expected):
        stream = stream_cls(config, authenticator=None)
        result = stream.request_params(stream_state, stream_slice, next_page_token)
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, current_state, latest_record, expected",
        [
            (Addresses, {}, {"updated_at": 2}, {"updated_at": 2}),
            (Charges, {"updated_at": 2}, {"updated_at": 3}, {"updated_at": 3}),
            (Customers, {"updated_at": 3}, {"updated_at": 4}, {"updated_at": 4}),
            (Discounts, {}, {"updated_at": 2}, {"updated_at": 2}),
            (Onetimes, {}, {"updated_at": 2}, {"updated_at": 2}),
            (Orders, {"updated_at": 5}, {"updated_at": 5}, {"updated_at": 5}),
            (Subscriptions, {"updated_at": 6}, {"updated_at": 7}, {"updated_at": 7}),
        ],
    )
    def test_get_updated_state(self, config, stream_cls, current_state, latest_record, expected):
        stream = stream_cls(config, authenticator=None)
        result = stream.get_updated_state(current_state, latest_record)
        assert result == expected
