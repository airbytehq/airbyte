#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk import AirbyteLogger
from source_file_secure import SourceFileSecure
from source_file_secure.source import LOCAL_STORAGE_NAME

local_storage_config = {
    "dataset_name": "test",
    "format": "csv",
    "reader_options": '{"sep": ",", "nrows": 20}',
    "url": "file:///tmp/fake_file.csv",
    "provider": {
        "storage": LOCAL_STORAGE_NAME.upper(),
    },
}


def test_local_storage_spec():
    """Checks spec properties"""
    source = SourceFileSecure()
    spec = source.spec(logger=AirbyteLogger())
    for provider in spec.connectionSpecification["properties"]["provider"]["oneOf"]:
        assert provider["properties"]["storage"]["const"] != LOCAL_STORAGE_NAME, "This connector shouldn't work with local files."


def test_local_storage_check():
    """Checks working with a local options"""
    source = SourceFileSecure()
    with pytest.raises(RuntimeError) as exc:
        source.check(logger=AirbyteLogger(), config=local_storage_config)
    assert "not supported" in str(exc.value)
