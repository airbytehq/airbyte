# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from unittest import TestCase

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import CONFIG, get_source, read_stream, stream_errors
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder, datadog_error


def _request() -> DatadogRequestBuilder:
    return DatadogRequestBuilder("v2/container_images").with_query_param("page[size]", 10000)


def _page(images: list[dict], meta: dict | None) -> DatadogPaginatedResponseBuilder:
    return DatadogPaginatedResponseBuilder("data").with_records(images).with_meta(meta)


class TestContainerImagesStream(TestCase):
    @HttpMocker()
    def test_reads_two_pages(self, http_mocker: HttpMocker) -> None:
        full_page = [{"id": f"image-{number}", "type": "container_image"} for number in range(10000)]
        last_page = [{"id": "image-10000", "type": "container_image"}]
        first_request = _request().build()
        second_request = _request().with_query_param("page[cursor]", "next-page").build()
        http_mocker.get(first_request, _page(full_page, {"pagination": {"next_cursor": "next-page"}}).build())
        http_mocker.get(second_request, _page(last_page, {"pagination": {"next_cursor": ""}}).build())

        output = read_stream("container_images")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == [record["id"] for record in full_page + last_page]
        http_mocker.assert_number_of_calls(first_request, 1)
        http_mocker.assert_number_of_calls(second_request, 1)

    @HttpMocker()
    def test_ends_without_a_next_cursor_and_on_a_null_meta(self, http_mocker: HttpMocker) -> None:
        # The vendor's own example of a last page carries no `next_cursor` at all.
        request = _request().build()
        http_mocker.get(
            request,
            [
                _page([{"id": "image-1"}], {"pagination": {"limit": 10000, "total": 1, "type": "cursor_limit"}}).build(),
                _page([{"id": "image-2"}], None).build(),
            ],
        )

        without_next_cursor = read_stream("container_images")
        null_meta = read_stream("container_images")

        assert without_next_cursor.errors == []
        assert null_meta.errors == []
        assert [message.record.data["id"] for message in without_next_cursor.records + null_meta.records] == ["image-1", "image-2"]
        http_mocker.assert_number_of_calls(request, 2)

    @HttpMocker()
    def test_ends_on_an_empty_page(self, http_mocker: HttpMocker) -> None:
        request = _request().build()
        http_mocker.get(request, _page([], {"pagination": {"next_cursor": "next-page"}}).build())

        output = read_stream("container_images")

        assert output.errors == []
        assert output.records == []
        http_mocker.assert_number_of_calls(request, 1)

    def test_is_keyed_on_id(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        assert next(stream.source_defined_primary_key for stream in catalog.streams if stream.name == "container_images") == [["id"]]

    @HttpMocker()
    def test_missing_permission_names_no_permission_because_the_spec_declares_none(self, http_mocker: HttpMocker) -> None:
        # `ListContainerImages` has an `OPEN` `x-permission` with an empty list.
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream("container_images", expecting_error=True)

        errors = stream_errors(output, "container_images")
        assert [(error.failure_type, error.message) for error in errors] == [
            (
                FailureType.config_error,
                "The Application Key lacks a permission that this stream requires: Forbidden, Failed permission authorization checks. "
                "Grant the missing permission to the Application Key in Datadog.",
            )
        ]
