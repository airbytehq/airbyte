# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import datetime
from unittest.mock import MagicMock, Mock

from source_gcs.helpers import GCSUploadableRemoteFile
from source_gcs.stream import GCSStream


def test_transform_record(zip_file, mocked_reader, logger):
    stream = GCSStream(
        config=Mock(),
        catalog_schema=Mock(),
        stream_reader=Mock(),
        availability_strategy=Mock(),
        discovery_policy=Mock(),
        parsers=Mock(),
        validation_policy=Mock(),
        errors_collector=Mock(),
        cursor=Mock(),
    )
    last_updated = zip_file.last_modified.isoformat()
    transformed_record = stream.transform_record({"field1": 1}, zip_file, last_updated)

    assert transformed_record["_ab_source_file_url"] == zip_file.displayed_uri
    assert transformed_record["_ab_source_file_url"] != zip_file.uri

    last_updated = datetime.today().isoformat()

    csv_file = GCSUploadableRemoteFile(uri="https://storage.googleapis.com/test/test", blob=MagicMock(), last_modified=last_updated)
    transformed_record = stream.transform_record({"field1": 1}, csv_file, last_updated)

    assert transformed_record["_ab_source_file_url"] == csv_file.uri
    assert transformed_record["_ab_source_file_url"] != csv_file.displayed_uri


def test_transform_record_service_account_uses_displayed_uri():
    """Service Account auth files must expose the URL without query params, not the signed URL."""
    stream = GCSStream(
        config=Mock(),
        catalog_schema=Mock(),
        stream_reader=Mock(),
        availability_strategy=Mock(),
        discovery_policy=Mock(),
        parsers=Mock(),
        validation_policy=Mock(),
        errors_collector=Mock(),
        cursor=Mock(),
    )
    signed_url = (
        "https://storage.googleapis.com/my-bucket/data.csv"
        "?X-Goog-Algorithm=GOOG4-RSA-SHA256"
        "&X-Goog-Credential=sa%40project.iam.gserviceaccount.com"
        "&X-Goog-Signature=abc123"
    )
    displayed_uri = "https://storage.googleapis.com/my-bucket/data.csv"
    last_updated = datetime.today().isoformat()

    sa_file = GCSUploadableRemoteFile(
        uri=signed_url,
        blob=MagicMock(),
        last_modified=last_updated,
        displayed_uri=displayed_uri,
    )
    record = stream.transform_record({"field1": 1}, sa_file, last_updated)

    assert record["_ab_source_file_url"] == displayed_uri
    assert "X-Goog-Credential" not in record["_ab_source_file_url"]
    assert "X-Goog-Signature" not in record["_ab_source_file_url"]
