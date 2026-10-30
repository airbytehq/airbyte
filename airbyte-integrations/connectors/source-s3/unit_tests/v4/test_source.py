#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from source_s3.v4 import Config, SourceS3, SourceS3StreamReader
from source_s3.v4.throttled_stream import ThrottledFileBasedStream

from airbyte_cdk.models import FailureType, Status
from airbyte_cdk.sources.file_based.config.csv_format import CsvFormat
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


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

    def test_when_spec_then_bucket_authentication_and_stream_fields_are_ordered(self) -> None:
        schema = self._source.spec().connectionSpecification
        properties = schema["properties"]
        stream_properties = properties["streams"]["items"]["properties"]

        assert "credentials" in schema["required"]
        assert properties["bucket"]["order"] == 0
        assert properties["credentials"]["order"] == 1
        assert properties["streams"]["title"] == "Streams"
        assert properties["streams"]["order"] == 5
        assert stream_properties["name"]["order"] == 0
        assert stream_properties["format"]["order"] == 1
        assert not {"aws_access_key_id", "aws_secret_access_key", "role_arn"} & properties.keys()

    def test_when_spec_then_groups_and_sections_are_kept_and_v3_fields_have_no_group(self) -> None:
        schema = self._source.spec().connectionSpecification

        assert [group["id"] for group in schema["groups"]] == ["bucket", "endpoint", "files", "start_date"]
        assert [section["id"] for section in schema["sections"]] == ["bucket", "files", "review"]
        assert all("group" not in schema["properties"][field] for field in _V3_FIELDS)

    def test_make_default_stream_returns_throttled_stream(self) -> None:
        stream_config = FileBasedStreamConfig(name="s", validation_policy="Emit Record", format=CsvFormat())
        cursor = Mock()

        stream = self._source._make_default_stream(stream_config, cursor, _ParsedConfig())

        assert isinstance(stream, ThrottledFileBasedStream)
        assert stream.config is stream_config
        assert stream.cursor is cursor


class CheckSectionTest(unittest.TestCase):
    """`check_section_connection`, the connector's part of the section-aware CHECK of the stepped setup form."""

    BUCKET_CONFIG = {
        "bucket": "acme-exports",
        "credentials": {"auth_type": "iam_user", "aws_access_key_id": "key", "aws_secret_access_key": "secret"},
        "endpoint": "https://my-s3-endpoint.com",
        "region_name": "eu-west-1",
    }
    FULL_CONFIG = {
        **BUCKET_CONFIG,
        "streams": [{"name": "exports", "format": {"filetype": "csv"}, "globs": ["**/*.csv"]}],
    }

    def setUp(self) -> None:
        self._stream_reader = Mock(spec=SourceS3StreamReader)
        self._source = SourceS3(self._stream_reader, Config, None, None, None)
        self._logger = logging.getLogger("test")

    def test_given_bucket_section_when_check_then_bucket_access_is_checked_without_streams(self) -> None:
        with patch("source_s3.v4.source.FileBasedSource.check_connection") as full_check:
            assert self._source.check_section_connection(self._logger, "bucket", self.BUCKET_CONFIG) == (True, None)

        full_check.assert_not_called()
        self._stream_reader.check_bucket_access.assert_called_once_with(self._logger)
        parsed_config = self._stream_reader.config
        assert isinstance(parsed_config, Config)
        assert parsed_config.bucket == "acme-exports"
        assert parsed_config.credentials.aws_access_key_id == "key"
        assert parsed_config.endpoint == "https://my-s3-endpoint.com"
        assert parsed_config.region_name == "eu-west-1"
        assert parsed_config.streams == []

    def test_given_bucket_section_when_bucket_is_not_accessible_then_error_propagates(self) -> None:
        self._stream_reader.check_bucket_access.side_effect = AirbyteTracedException(
            message="The bucket acme-exports does not exist.", failure_type=FailureType.config_error
        )

        with pytest.raises(AirbyteTracedException, match="The bucket acme-exports does not exist."):
            self._source.check_section_connection(self._logger, "bucket", self.BUCKET_CONFIG)

    def test_given_bucket_section_when_a_required_field_is_missing_then_error_names_it(self) -> None:
        for field in ("bucket", "credentials"):
            config = {key: value for key, value in self.BUCKET_CONFIG.items() if key != field}
            with pytest.raises(AirbyteTracedException) as exc_info:
                self._source.check_section_connection(self._logger, "bucket", config)
            assert exc_info.value.failure_type == FailureType.config_error
            assert exc_info.value.message == f"The 'bucket' section check requires the '{field}' field."
        self._stream_reader.check_bucket_access.assert_not_called()

    def test_given_bucket_section_when_credentials_are_invalid_then_config_error(self) -> None:
        config = {**self.BUCKET_CONFIG, "credentials": {"auth_type": "iam_user"}}

        with pytest.raises(AirbyteTracedException) as exc_info:
            self._source.check_section_connection(self._logger, "bucket", config)

        assert exc_info.value.failure_type == FailureType.config_error
        assert exc_info.value.message.startswith("Invalid configuration for the 'bucket' section: ")
        assert "aws_access_key_id" in exc_info.value.message
        self._stream_reader.check_bucket_access.assert_not_called()

    @patch("source_s3.v4.source.is_cloud_environment", return_value=True)
    @patch("source_s3.v4.config.is_cloud_environment", return_value=True)
    def test_given_bucket_section_on_cloud_when_endpoint_is_http_then_config_error(self, *_) -> None:
        config = {**self.BUCKET_CONFIG, "endpoint": "http://my-s3-endpoint.com"}  # ignore-https-check

        with pytest.raises(AirbyteTracedException) as exc_info:
            self._source.check_section_connection(self._logger, "bucket", config)

        assert exc_info.value.failure_type == FailureType.config_error
        assert "The endpoint must be a secure HTTPS endpoint." in exc_info.value.message
        self._stream_reader.check_bucket_access.assert_not_called()

    def test_given_files_section_when_check_then_full_check(self) -> None:
        with patch("source_s3.v4.source.FileBasedSource.check_connection", return_value=(True, None)) as full_check:
            assert self._source.check_section_connection(self._logger, "files", self.FULL_CONFIG) == (True, None)

        full_check.assert_called_once_with(self._logger, self.FULL_CONFIG)
        self._stream_reader.check_bucket_access.assert_not_called()

    def test_given_review_section_when_check_section_then_config_error(self) -> None:
        # The review section is the last one: the CDK runs the full check for it and never calls the section check.
        with pytest.raises(AirbyteTracedException) as exc_info:
            self._source.check_section_connection(self._logger, "review", self.FULL_CONFIG)

        assert exc_info.value.failure_type == FailureType.config_error
        assert exc_info.value.message == "Section 'review' has no section check."

    def test_given_section_when_check_section_then_status_is_wrapped(self) -> None:
        self._stream_reader.check_bucket_access.return_value = None

        status = self._source.check_section(self._logger, "bucket", self.BUCKET_CONFIG)

        assert status.status == Status.SUCCEEDED

    @patch("source_s3.v4.source.emit_configuration_as_airbyte_control_message")
    def test_given_section_config_without_streams_when_read_config_then_it_is_a_v4_config(self, emit_config_mock) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text(json.dumps({"check-section": "bucket", **self.BUCKET_CONFIG}))
            config = self._source.read_config(str(config_path))

        assert config == {"check-section": "bucket", **self.BUCKET_CONFIG}
        emit_config_mock.assert_not_called()
