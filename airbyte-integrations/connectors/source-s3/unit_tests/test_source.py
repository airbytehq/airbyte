#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock, patch

import pytest
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import ConnectorSpecification
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
    "delimiter, quote_char, escape_char, encoding, error_type",
    [
        ("string", "'", None, "utf8", ValueError),
        ("\n", "'", None, "utf8", ValueError),
        (",", ";,", None, "utf8", ValueError),
        (",", "'", "escape", "utf8", ValueError),
        (",", "'", None, "utf888", LookupError)
    ],
    ids=[
        "long_delimiter",
        "forbidden_delimiter_symbol",
        "long_quote_char",
        "long_escape_char",
        "unknown_encoding"
    ],
)
def test_check_connection_csv_validation_exception(delimiter, quote_char, escape_char, encoding, error_type):
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
        }
    }
    ok, error_msg = SourceS3().check_connection(logger, config=config)

    assert not ok
    assert error_msg
    assert isinstance(error_msg, error_type)


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
