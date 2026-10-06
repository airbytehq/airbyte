#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
from unittest import TestCase
from unittest.mock import patch

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source

from .config import ConfigBuilder


def _create_catalog(sync_mode: SyncMode = SyncMode.full_refresh):
    return CatalogBuilder().with_stream(name="contacts", sync_mode=sync_mode).build()


@freezegun.freeze_time("2024-01-15T00:00:00Z")
class TestContactsStream(TestCase):
    """Tests for the contacts stream which uses AsyncRetriever with CSV decoder and KeysToLower transformation.

    Note: The contacts stream uses GzipDecoder wrapping CsvDecoder in the manifest, but HttpMocker
    doesn't properly handle binary gzip responses. We use plain CSV text here which still validates
    the AsyncRetriever flow (creation -> polling -> download) and KeysToLower transformation.
    """

    @HttpMocker()
    def test_read_full_refresh_with_transformation(self, http_mocker: HttpMocker):
        """Test full refresh sync verifying KeysToLower transformation is applied."""
        config = ConfigBuilder().build()

        # Step 1: Mock the export creation request (POST)
        http_mocker.post(
            HttpRequest(
                url="https://api.sendgrid.com/v3/marketing/contacts/exports",
            ),
            HttpResponse(
                body=json.dumps({"id": "export_job_123", "status": "pending", "urls": [], "message": "Export job created"}),
                status_code=202,
            ),
        )

        # Step 2: Mock the polling request (GET status) - return "ready" status
        http_mocker.get(
            HttpRequest(
                url="https://api.sendgrid.com/v3/marketing/contacts/exports/export_job_123",
            ),
            HttpResponse(
                body=json.dumps(
                    {
                        "id": "export_job_123",
                        "status": "ready",
                        "urls": ["https://sendgrid-export.s3.amazonaws.com/contacts_export.csv.gz"],
                        "message": "Export ready for download",
                    }
                ),
                status_code=200,
            ),
        )

        # Step 3: Mock the download request - return plain CSV with uppercase field names
        # The KeysToLower transformation should convert these to lowercase
        # Note: Using plain CSV instead of gzipped because HttpMocker doesn't handle binary responses
        csv_content = """CONTACT_ID,EMAIL,FIRST_NAME,LAST_NAME,CREATED_AT,UPDATED_AT
contact_123,test@example.com,John,Doe,2024-01-10T10:00:00Z,2024-01-12T15:30:00Z
contact_456,another@example.com,Jane,Smith,2024-01-11T11:00:00Z,2024-01-13T16:45:00Z"""

        http_mocker.get(
            HttpRequest(
                url="https://sendgrid-export.s3.amazonaws.com/contacts_export.csv.gz",
            ),
            HttpResponse(
                body=csv_content,
                status_code=200,
            ),
        )

        source = get_source(config)
        with patch("time.sleep", return_value=None):
            actual_messages = read(source, config=config, catalog=_create_catalog())

        # Verify records were returned
        assert len(actual_messages.records) == 2

        # Verify KeysToLower transformation was applied - field names should be lowercase
        first_record = actual_messages.records[0].record.data
        assert "contact_id" in first_record, "KeysToLower transformation should lowercase field names"
        assert "email" in first_record
        assert "first_name" in first_record
        assert "last_name" in first_record

        # Verify uppercase field names are NOT present (transformation worked)
        assert "CONTACT_ID" not in first_record, "Uppercase field names should be transformed to lowercase"
        assert "EMAIL" not in first_record
        assert "FIRST_NAME" not in first_record

        # Verify specific record values
        assert first_record["contact_id"] == "contact_123"
        assert first_record["email"] == "test@example.com"
        assert first_record["first_name"] == "John"
        assert first_record["last_name"] == "Doe"

        # Verify second record
        second_record = actual_messages.records[1].record.data
        assert second_record["contact_id"] == "contact_456"
        assert second_record["email"] == "another@example.com"
