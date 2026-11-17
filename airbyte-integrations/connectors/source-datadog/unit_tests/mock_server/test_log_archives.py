# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
from typing import Any
from unittest import TestCase

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import CONFIG, get_source, read_stream, stream_errors
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder, datadog_error


def _request() -> DatadogRequestBuilder:
    return DatadogRequestBuilder("v2/logs/config/archives")


def _archive(archive_id: str, destination: dict[str, Any] | None) -> dict[str, Any]:
    return {"id": archive_id, "type": "archives", "attributes": {"name": archive_id, "query": "*", "destination": destination}}


S3_WITH_AN_ACCESS_KEY = _archive(
    "s3-access-key", {"type": "s3", "bucket": "logs", "path": "/archive", "integration": {"access_key_id": "fake-access-key-id"}}
)
S3_WITH_A_ROLE = _archive(
    "s3-role", {"type": "s3", "bucket": "logs", "integration": {"account_id": "123456789012", "role_name": "datadog-archives"}}
)
AZURE = _archive(
    "azure",
    {
        "type": "azure",
        "container": "logs",
        "storage_account": "datadogarchives",
        "integration": {"tenant_id": "fake-tenant-id", "client_id": "fake-client-id"},
    },
)
GCS = _archive(
    "gcs",
    {"type": "gcs", "bucket": "logs", "integration": {"client_email": "archives@project.iam.gserviceaccount.com", "project_id": "project"}},
)
WITHOUT_A_DESTINATION = _archive("without-destination", None)


class TestLogArchivesStream(TestCase):
    @HttpMocker()
    def test_reads_every_archive_in_one_request(self, http_mocker: HttpMocker) -> None:
        # `ListLogsArchives` takes no paging parameter and returns every archive.
        request = _request().build()
        archives = [S3_WITH_AN_ACCESS_KEY, S3_WITH_A_ROLE, AZURE, GCS, WITHOUT_A_DESTINATION]
        http_mocker.get(request, DatadogPaginatedResponseBuilder("data").with_records(archives).build())

        output = read_stream("log_archives")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == [archive["id"] for archive in archives]
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_removes_the_access_key_id_of_an_s3_destination(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), DatadogPaginatedResponseBuilder("data").with_records([S3_WITH_AN_ACCESS_KEY]).build())

        output = read_stream("log_archives")

        assert output.errors == []
        assert [message.record.data["attributes"]["destination"] for message in output.records] == [
            {"type": "s3", "bucket": "logs", "path": "/archive", "integration": {}}
        ]
        assert "fake-access-key-id" not in json.dumps([message.record.data for message in output.records])

    @HttpMocker()
    def test_keeps_the_other_destinations_whole(self, http_mocker: HttpMocker) -> None:
        archives = [S3_WITH_A_ROLE, AZURE, GCS, WITHOUT_A_DESTINATION]
        http_mocker.get(_request().build(), DatadogPaginatedResponseBuilder("data").with_records(archives).build())

        output = read_stream("log_archives")

        assert output.errors == []
        assert [message.record.data for message in output.records] == archives

    def test_declares_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        assert [stream.source_defined_primary_key for stream in catalog.streams if stream.name == "log_archives"] == [[["id"]]]

    @HttpMocker()
    def test_missing_permission_names_logs_read_archives(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream("log_archives", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "log_archives")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the logs_read_archives permission: Forbidden, Failed permission authorization checks. "
                "Grant logs_read_archives to the Application Key in Datadog.",
            )
        ]
