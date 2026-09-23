# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from http import HTTPStatus
from unittest import TestCase
from unittest.mock import patch

import jwt

from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import get_source

from .config import ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import error_response, fixture_names, fixture_response
from .utils import read_output


_STREAM_NAME = "list_id_apps"


class TestListIdAppsStream(TestCase):
    def test_manifest_loads_all_streams(self) -> None:
        config = ConfigBuilder().build()
        streams = get_source(config).streams(config=config)

        stream_names = {stream.name for stream in streams}
        assert len(streams) == 29
        assert stream_names == fixture_names()
        assert stream_names >= {
            _STREAM_NAME,
            "customer_reviews_per_app",
            "sales_report",
            "finance_report",
            "app_store_installations_and_deletions",
            "app_download",
        }

    def test_jwt_authenticator_uses_apple_claims(self) -> None:
        config = ConfigBuilder().build()
        source = get_source(config)
        stream = next(stream for stream in source.streams(config=config) if stream.name == _STREAM_NAME)
        partition = next(iter(stream.generate_partitions()))

        token = partition._retriever.requester._request_headers()["Authorization"].removeprefix("Bearer ")
        header = jwt.get_unverified_header(token)
        claims = jwt.decode(token, options={"verify_signature": False, "verify_aud": False})

        assert header == {"alg": "ES256", "kid": "TESTKEY123", "typ": "JWT"}
        assert claims["iss"] == config["iss"]
        assert claims["aud"] == "appstoreconnect-v1"
        assert claims["exp"] - claims["iat"] == 900

    @HttpMocker()
    def test_read_records_and_transform_attributes(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(RequestBuilder.apps_endpoint().build(), fixture_response(_STREAM_NAME))

        output = read_output(ConfigBuilder(), _STREAM_NAME)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["id"] == "app-1"
        assert record["bundleId"] == "com.example.app-1"
        assert record["streamlinedPurchasingEnabled"] is True

    @HttpMocker()
    def test_pagination_follows_next_link(self, http_mocker: HttpMocker) -> None:
        next_url = "https://api.appstoreconnect.apple.com/v1/apps?cursor=PAGE_TWO"
        http_mocker.get(
            RequestBuilder.apps_endpoint().build(),
            fixture_response(_STREAM_NAME, next_url=next_url),
        )
        http_mocker.get(
            RequestBuilder.apps_endpoint().with_cursor("PAGE_TWO").build(),
            fixture_response(_STREAM_NAME, id_suffix="-page-2"),
        )

        output = read_output(ConfigBuilder(), _STREAM_NAME)

        assert [record.record.data["id"] for record in output.records] == ["app-1", "app-1-page-2"]

    @HttpMocker()
    def test_not_found_is_ignored(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            RequestBuilder.apps_endpoint().build(),
            error_response(HTTPStatus.NOT_FOUND),
        )

        output = read_output(ConfigBuilder(), _STREAM_NAME)

        assert not output.records

    @HttpMocker()
    def test_server_error_is_retried(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            RequestBuilder.apps_endpoint().build(),
            [error_response(HTTPStatus.INTERNAL_SERVER_ERROR), fixture_response(_STREAM_NAME)],
        )

        with patch("airbyte_cdk.sources.streams.http.rate_limiting.time.sleep"):
            output = read_output(ConfigBuilder(), _STREAM_NAME)

        assert output.records[0].record.data["id"] == "app-1"
