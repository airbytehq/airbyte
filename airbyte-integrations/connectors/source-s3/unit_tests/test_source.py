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


def test_check_connection(config):
    instance = SourceS3()
    with patch.object(instance.stream_class, "filepath_iterator", MagicMock()):
        ok, error_msg = instance.check_connection(logger, config=config)

    assert ok
    assert not error_msg


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
