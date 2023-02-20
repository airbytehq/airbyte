#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock, patch

import pytest
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import ConnectorSpecification
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from source_s3 import SourceS3
from source_s3.source_files_abstract.spec import SourceFilesAbstractSpec

logger = AirbyteLogger()


def test_transform_backslash_t_to_tab(tmp_path):
    config_file = tmp_path / "config.json"
    with open(config_file, "w") as fp:
        json.dump({"format": {"delimiter": "\\t"}}, fp)
    source = SourceS3()
    config = source.read_config(config_file)
    assert config["format"]["delimiter"] == "\t"


def test_check_connection_empty_config():
    config = {}
    ok, error_msg = SourceS3().check_connection(logger, config=config)

    assert not ok
    assert error_msg


def test_check_connection_exception(config):
    ok, error_msg = SourceS3().check_connection(logger, config=config)

    assert not ok
    assert error_msg


@pytest.mark.parametrize(
    "delimiter, quote_char, escape_char, encoding, read_options, convert_options",
    [
        ("string", "'", None, "utf8", "{}", "{}"),
        ("\n", "'", None, "utf8", "{}", "{}"),
        (",", ";,", None, "utf8", "{}", "{}"),
        (",", "'", "escape", "utf8", "{}", "{}"),
        (",", "'", None, "utf888", "{}", "{}"),
        (",", "'", None, "utf8", "{'compression': true}", "{}"),
        (",", "'", None, "utf8", "{}", "{'compression: true}"),
    ],
    ids=[
        "long_delimiter",
        "forbidden_delimiter_symbol",
        "long_quote_char",
        "long_escape_char",
        "unknown_encoding",
        "invalid read options",
        "invalid convert options"
    ],
)
def test_check_connection_csv_validation_exception(delimiter, quote_char, escape_char, encoding, read_options, convert_options):
    config = {
        "dataset": "test",
        "provider": {
            "storage": "S3",
            "bucket": "test-source-s3",
            "aws_access_key_id": "key_id",
            "aws_secret_access_key": "access_key",
            "path_prefix": ""
        },
        "path_pattern": "simple_test*.csv",
        "schema": "{}",
        "format": {
            "filetype": "csv",
            "delimiter": delimiter,
            "quote_char": quote_char,
            "escape_char": escape_char,
            "encoding": encoding,
            "advanced_options": read_options,
            "additional_reader_options": convert_options
        }
    }
    ok, error_msg = SourceS3().check_connection(logger, config=config)

    assert not ok
    assert error_msg
    assert isinstance(error_msg, AirbyteTracedException)


def test_check_connection(config):
    instance = SourceS3()
    with patch.object(instance.stream_class, "filepath_iterator", MagicMock()):
        ok, error_msg = instance.check_connection(logger, config=config)

    assert not ok
    assert error_msg


def test_streams(config):
    instance = SourceS3()
    assert len(instance.streams(config)) == 1


def test_spec():
    spec = SourceS3().spec()

    assert isinstance(spec, ConnectorSpecification)


def test_check_provider_added():
    with pytest.raises(Exception):
        SourceFilesAbstractSpec.check_provider_added({"properties": []})


def test_change_format_to_oneOf():
    assert SourceFilesAbstractSpec.change_format_to_oneOf({"properties": {"format": {"oneOf": ""}}})
