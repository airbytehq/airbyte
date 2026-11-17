# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from unittest import TestCase

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import CONFIG, get_source, read_stream, stream_errors
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder, datadog_error


def _request() -> DatadogRequestBuilder:
    return (
        DatadogRequestBuilder("v1/hosts")
        .with_query_param("count", 1000)
        .with_query_param("include_hosts_metadata", "true")
        .with_query_param("include_muted_hosts_data", "true")
    )


def _page(hosts: list[dict]) -> DatadogPaginatedResponseBuilder:
    return DatadogPaginatedResponseBuilder("host_list").with_records(hosts)


class TestHostsStream(TestCase):
    @HttpMocker()
    def test_reads_two_pages(self, http_mocker: HttpMocker) -> None:
        full_page = [{"id": number, "name": f"host-{number}"} for number in range(1000)]
        last_page = [{"id": 1000, "name": "host-1000"}]
        first_request = _request().build()
        second_request = _request().with_query_param("start", 1000).build()
        http_mocker.get(first_request, _page(full_page).build())
        http_mocker.get(second_request, _page(last_page).build())

        output = read_stream("hosts")

        assert output.errors == []
        assert [message.record.data["name"] for message in output.records] == [host["name"] for host in full_page + last_page]
        http_mocker.assert_number_of_calls(first_request, 1)
        http_mocker.assert_number_of_calls(second_request, 1)

    @HttpMocker()
    def test_ends_on_an_empty_page_after_a_full_one(self, http_mocker: HttpMocker) -> None:
        full_page = [{"id": number, "name": f"host-{number}"} for number in range(1000)]
        empty_page = _request().with_query_param("start", 1000).build()
        http_mocker.get(_request().build(), _page(full_page).build())
        http_mocker.get(empty_page, _page([]).build())

        output = read_stream("hosts")

        assert output.errors == []
        assert len(output.records) == 1000
        http_mocker.assert_number_of_calls(empty_page, 1)

    @HttpMocker()
    def test_keys_a_host_on_its_name_because_an_ec2_host_has_no_id(self, http_mocker: HttpMocker) -> None:
        # For an Amazon EC2 instance Datadog replaces `id` with `aws_id` (`ListHosts`).
        ec2_host = {"aws_id": "i-0123456789abcdef0", "name": "i-0123456789abcdef0"}
        http_mocker.get(_request().build(), _page([ec2_host, {"id": 42, "name": "web-1"}]).build())

        output = read_stream("hosts")
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        assert output.errors == []
        assert [message.record.data["name"] for message in output.records] == ["i-0123456789abcdef0", "web-1"]
        assert next(stream.source_defined_primary_key for stream in catalog.streams if stream.name == "hosts") == [["name"]]

    @HttpMocker()
    def test_missing_permission_names_hosts_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream("hosts", expecting_error=True)

        errors = stream_errors(output, "hosts")
        assert [(error.failure_type, error.message) for error in errors] == [
            (
                FailureType.config_error,
                "The Application Key lacks the hosts_read permission: Forbidden, Failed permission authorization checks. "
                "Grant hosts_read to the Application Key in Datadog.",
            )
        ]
