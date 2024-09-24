# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import datetime
from unittest.mock import Mock

from source_gcs.helpers import GCSRemoteFile
from source_gcs.stream import GCSStream


def test_transform_record(zip_file, mocked_reader, logger):
    stream = GCSStream(
        config=Mock(), catalog_schema=Mock(), stream_reader=Mock(), availability_strategy=Mock(), discovery_policy=Mock(),parsers=Mock(),
        validation_policy=Mock(), errors_collector=Mock(), cursor=Mock()
    )
    last_updated = zip_file.last_modified.isoformat()
    transformed_record = stream.transform_record({"field1": 1}, zip_file, last_updated)

    assert transformed_record["_ab_source_file_url"] == zip_file.displayed_uri
    assert transformed_record["_ab_source_file_url"] != zip_file.uri

    last_updated = datetime.today().isoformat()
    csv_file = GCSRemoteFile(
        uri="https://storage.googleapis.com/test/test",
        last_modified=last_updated,
        mime_type = "csv"
    )
    transformed_record = stream.transform_record({"field1": 1}, csv_file, last_updated)

    assert transformed_record["_ab_source_file_url"] == csv_file.uri
    assert transformed_record["_ab_source_file_url"] != csv_file.displayed_uri
