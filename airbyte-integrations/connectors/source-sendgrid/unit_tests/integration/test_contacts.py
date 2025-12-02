# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from http import HTTPStatus
from typing import List, Optional
from unittest import TestCase

import freezegun

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker

from .config import ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import (
    CONTACTS_DOWNLOAD_URL,
    contacts_download_response,
    contacts_export_create_response,
    contacts_export_status_response,
    error_response,
)
from .utils import config, read_output


_STREAM_NAME = "contacts"


def _read(
    config_builder: ConfigBuilder,
    sync_mode: SyncMode = SyncMode.full_refresh,
    state: Optional[List[AirbyteStateMessage]] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    return read_output(
        config_builder=config_builder,
        stream_name=_STREAM_NAME,
        sync_mode=sync_mode,
        state=state,
        expecting_exception=expecting_exception,
    )


@freezegun.freeze_time("2024-01-31T00:00:00Z")
class TestContactsStream(TestCase):
    """
    Tests for the contacts stream which uses AsyncRetriever.
    The contacts stream requires:
    1. POST to create an export job
    2. GET to poll for export status
    3. Download the exported data from URLs
    """

    @HttpMocker()
    def test_read_records_async_export(self, http_mocker: HttpMocker) -> None:
        """Test the async export flow for contacts stream"""
        export_id = "export-job-123"

        # Mock the export creation endpoint
        http_mocker.post(
            RequestBuilder.contacts_export_endpoint().with_any_query_params().build(),
            contacts_export_create_response(export_id=export_id),
        )

        # Mock the export status endpoint - returns ready status with download URLs
        http_mocker.get(
            RequestBuilder.contacts_export_status_endpoint(export_id).with_any_query_params().build(),
            contacts_export_status_response(
                export_id=export_id,
                status="ready",
                urls=[CONTACTS_DOWNLOAD_URL],
            ),
        )

        # Mock the download endpoint - returns gzipped CSV data
        http_mocker.get(
            RequestBuilder.contacts_download_endpoint(CONTACTS_DOWNLOAD_URL).build(),
            contacts_download_response(),
        )

        output = _read(config_builder=config())
        assert len(output.records) >= 1

    @HttpMocker()
    def test_export_pending_then_ready(self, http_mocker: HttpMocker) -> None:
        """Test export status polling when initially pending"""
        export_id = "export-job-456"

        # Mock the export creation endpoint
        http_mocker.post(
            RequestBuilder.contacts_export_endpoint().with_any_query_params().build(),
            contacts_export_create_response(export_id=export_id),
        )

        # Mock the export status endpoint - first pending, then ready
        http_mocker.get(
            RequestBuilder.contacts_export_status_endpoint(export_id).with_any_query_params().build(),
            [
                contacts_export_status_response(export_id=export_id, status="pending", urls=[]),
                contacts_export_status_response(
                    export_id=export_id,
                    status="ready",
                    urls=[CONTACTS_DOWNLOAD_URL],
                ),
            ],
        )

        # Mock the download endpoint - returns gzipped CSV data
        http_mocker.get(
            RequestBuilder.contacts_download_endpoint(CONTACTS_DOWNLOAD_URL).build(),
            contacts_download_response(),
        )

        output = _read(config_builder=config())
        assert len(output.records) >= 1


@freezegun.freeze_time("2024-01-31T00:00:00Z")
class TestContactsErrors(TestCase):
    @HttpMocker()
    def test_error_401_unauthorized(self, http_mocker: HttpMocker) -> None:
        """Test 401 error handling on export creation"""
        http_mocker.post(
            RequestBuilder.contacts_export_endpoint().with_any_query_params().build(),
            error_response(HTTPStatus.UNAUTHORIZED),
        )

        output = _read(config_builder=config(), expecting_exception=True)
        assert len(output.records) == 0

    @HttpMocker()
    def test_error_403_forbidden(self, http_mocker: HttpMocker) -> None:
        """Test 403 error handling on export creation"""
        http_mocker.post(
            RequestBuilder.contacts_export_endpoint().with_any_query_params().build(),
            error_response(HTTPStatus.FORBIDDEN),
        )

        output = _read(config_builder=config(), expecting_exception=True)
        assert len(output.records) == 0
