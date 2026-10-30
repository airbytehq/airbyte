#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from source_s3.v4 import Config, SourceS3, SourceS3StreamReader
from source_s3.v4.throttled_stream import ThrottledFileBasedStream

from airbyte_cdk.sources.file_based.config.csv_format import CsvFormat
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig


_V3_FIELDS = ["dataset", "format", "path_pattern", "provider", "schema"]
TEST_FILES_FOLDER = Path(__file__).resolve().parent.parent.joinpath("sample_files")


class _ParsedConfig:
    delivery_method = object()


class SourceTest(unittest.TestCase):
    def setUp(self) -> None:
        self._stream_reader = Mock(spec=SourceS3StreamReader)
        self._source = SourceS3(
            self._stream_reader,
            Config,
            SourceS3.read_catalog(str(TEST_FILES_FOLDER.joinpath("catalog.json"))),
            SourceS3.read_config(str(TEST_FILES_FOLDER.joinpath("v3_config.json"))),
            None,
        )

    @patch("source_s3.v4.source.emit_configuration_as_airbyte_control_message")
    def test_given_config_is_v3_when_read_config_then_emit_new_config(self, emit_config_mock) -> None:
        config = self._source.read_config(str(TEST_FILES_FOLDER.joinpath("v3_config.json")))
        assert emit_config_mock.call_count == 1
        assert config["credentials"] == {
            "auth_type": "iam_user",
            "aws_access_key_id": "a key id",
            "aws_secret_access_key": "an access key",
        }

    @patch("source_s3.v4.source.emit_configuration_as_airbyte_control_message")
    def test_given_config_is_v4_when_read_config_then_do_not_emit_new_config(self, emit_config_mock) -> None:
        config = self._source.read_config(str(TEST_FILES_FOLDER.joinpath("v4_config.json")))
        assert emit_config_mock.call_count == 0
        assert config["credentials"] == {"auth_type": "default_credentials"}

    @patch("source_s3.v4.source.emit_configuration_as_airbyte_control_message")
    def test_given_config_is_flat_v4_when_read_config_then_migrate_credentials(self, emit_config_mock) -> None:
        legacy_config = {
            "bucket": "a-bucket",
            "streams": [],
            "aws_access_key_id": "access",
            "aws_secret_access_key": "secret",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text(json.dumps(legacy_config))
            migrated_config = self._source.read_config(str(config_path))

        expected_config = {
            "bucket": "a-bucket",
            "streams": [],
            "credentials": {"auth_type": "iam_user", "aws_access_key_id": "access", "aws_secret_access_key": "secret"},
        }
        assert migrated_config == expected_config
        emit_config_mock.assert_called_once_with(expected_config)

    def test_when_spec_then_v3_fields_not_required(self) -> None:
        spec = self._source.spec()
        assert all(field not in spec.connectionSpecification["required"] for field in _V3_FIELDS)

    def test_when_spec_then_v3_fields_are_hidden(self) -> None:
        spec = self._source.spec()
        assert all(spec.connectionSpecification["properties"][field]["airbyte_hidden"] for field in _V3_FIELDS)

    def test_when_spec_then_v3_fields_descriptions_are_prefixed_with_deprecation_warning(self) -> None:
        spec = self._source.spec()
        assert all(
            spec.connectionSpecification["properties"][field]["description"].startswith("Deprecated and will be removed soon")
            for field in _V3_FIELDS
        )

    def test_when_spec_then_v3_nested_fields_are_not_required(self) -> None:
        spec = self._source.spec()
        assert not spec.connectionSpecification["properties"]["provider"]["required"]

    def test_when_spec_then_authentication_and_stream_fields_are_ordered(self) -> None:
        schema = self._source.spec().connectionSpecification
        properties = schema["properties"]
        stream_properties = properties["streams"]["items"]["properties"]

        assert "credentials" in schema["required"]
        assert properties["credentials"]["order"] == 0
        assert properties["bucket"]["order"] == 1
        assert properties["streams"]["title"] == "Streams"
        assert properties["streams"]["order"] == 2
        assert stream_properties["name"]["order"] == 0
        assert stream_properties["format"]["order"] == 1
        assert not {"aws_access_key_id", "aws_secret_access_key", "role_arn"} & properties.keys()

    def test_make_default_stream_returns_throttled_stream(self) -> None:
        stream_config = FileBasedStreamConfig(name="s", validation_policy="Emit Record", format=CsvFormat())
        cursor = Mock()

        stream = self._source._make_default_stream(stream_config, cursor, _ParsedConfig())

        assert isinstance(stream, ThrottledFileBasedStream)
        assert stream.config is stream_config
        assert stream.cursor is cursor
