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


def test_transform_record_service_account_uses_canonical_https_url():
    """Service Account auth sets _ab_source_file_url to the canonical HTTPS path.

    As of 0.10.29, the stream reader sets displayed_uri to the clean HTTPS URL
    (no credentials, no query string) for Service Account auth. transform_record
    prefers displayed_uri over uri, so _ab_source_file_url is always credential-free.
    """
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
    canonical_url = "https://storage.googleapis.com/my-bucket/data.csv"
    last_updated = datetime.today().isoformat()

    sa_file = GCSUploadableRemoteFile(
        uri="gs://my-bucket/data.csv",
        blob=MagicMock(),
        last_modified=last_updated,
        displayed_uri=canonical_url,
    )
    record = stream.transform_record({"field1": 1}, sa_file, last_updated)

    assert record["_ab_source_file_url"] == canonical_url
    assert "X-Goog-Credential" not in record["_ab_source_file_url"]
    assert "X-Goog-Signature" not in record["_ab_source_file_url"]
    assert "X-Goog-Algorithm" not in record["_ab_source_file_url"]


def test_transform_record_oauth_uses_gs_uri():
    """OAuth auth sets _ab_source_file_url to the gs:// URI (displayed_uri is None)."""
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
    gs_uri = "gs://my-bucket/data.csv"
    last_updated = datetime.today().isoformat()

    oauth_file = GCSUploadableRemoteFile(
        uri=gs_uri,
        blob=MagicMock(),
        last_modified=last_updated,
        displayed_uri=None,
    )
    record = stream.transform_record({"field1": 1}, oauth_file, last_updated)

    assert record["_ab_source_file_url"] == gs_uri
