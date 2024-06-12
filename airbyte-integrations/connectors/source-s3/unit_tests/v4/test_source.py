#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from source_s3.v4 import Config, SourceS3, SourceS3StreamReader

_V3_FIELDS = ["dataset", "format", "path_pattern", "provider", "schema"]
TEST_FILES_FOLDER = Path(__file__).resolve().parent.parent.joinpath("sample_files")


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
        self._source.read_config(str(TEST_FILES_FOLDER.joinpath("v3_config.json")))
        assert emit_config_mock.call_count == 1

    @patch("source_s3.v4.source.emit_configuration_as_airbyte_control_message")
    def test_given_config_is_v4_when_read_config_then_do_not_emit_new_config(self, emit_config_mock) -> None:
        self._source.read_config(str(TEST_FILES_FOLDER.joinpath("v4_config.json")))
        assert emit_config_mock.call_count == 0

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
