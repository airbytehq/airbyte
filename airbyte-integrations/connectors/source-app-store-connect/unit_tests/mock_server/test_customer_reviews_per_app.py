# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from http import HTTPStatus
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from .analytics_helpers import APP_ID
from .config import ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import error_response, fixture_response
from .utils import latest_stream_state, read_output


_STREAM_NAME = "customer_reviews_per_app"


def _reviews_request() -> RequestBuilder:
    return RequestBuilder.customer_reviews_endpoint(APP_ID).with_query_param("sort", "-createdDate").with_query_param("limit", "200")


def _mock_app(http_mocker: HttpMocker) -> None:
    http_mocker.get(
        RequestBuilder.apps_endpoint().build(),
        fixture_response("list_id_apps"),
    )


class TestCustomerReviewsPerAppStream(TestCase):
    @HttpMocker()
    def test_incremental_read_emits_state(self, http_mocker: HttpMocker) -> None:
        created_date = "2024-01-03T00:00:00Z"
        previous_date = "2024-01-02T00:00:00Z"
        config = ConfigBuilder().with_value("reviews_start_date", previous_date)
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"createdDate": previous_date}).build()
        _mock_app(http_mocker)
        http_mocker.get(_reviews_request().build(), fixture_response(_STREAM_NAME))

        output = read_output(config, _STREAM_NAME, SyncMode.incremental, state)

        assert len(output.records) == 1
        assert output.records[0].record.data["app_id"] == APP_ID
        assert output.records[0].record.data["createdDate"] == created_date
        assert latest_stream_state(output, "createdDate") == created_date.removesuffix("Z") + "+0000"

    @HttpMocker()
    def test_pagination_follows_next_link(self, http_mocker: HttpMocker) -> None:
        next_url = f"{_reviews_request().url}?cursor=PAGE_TWO"
        _mock_app(http_mocker)
        http_mocker.get(
            _reviews_request().build(),
            fixture_response(_STREAM_NAME, next_url=next_url),
        )
        http_mocker.get(
            _reviews_request().with_cursor("PAGE_TWO").build(),
            fixture_response(_STREAM_NAME, id_suffix="-page-2"),
        )

        config = ConfigBuilder().with_value("reviews_start_date", "2024-01-01T00:00:00Z")
        output = read_output(config, _STREAM_NAME)

        assert {record.record.data["id"] for record in output.records} == {"review-1", "review-1-page-2"}

    @HttpMocker()
    def test_not_found_is_ignored(self, http_mocker: HttpMocker) -> None:
        _mock_app(http_mocker)
        http_mocker.get(_reviews_request().build(), error_response(HTTPStatus.NOT_FOUND))

        output = read_output(ConfigBuilder(), _STREAM_NAME)

        assert not output.records
