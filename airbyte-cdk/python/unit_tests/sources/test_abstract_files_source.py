#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import logging
import tempfile
from unittest.mock import MagicMock, patch

import pendulum
from airbyte_cdk.models import ConnectorSpecification
from airbyte_cdk.sources.abstract_files_source import AbstractFilesSource
from airbyte_cdk.sources.streams.files import FileInfo, FilesSpec, IncrementalFilesStream
from pytest import fixture

logger = logging.getLogger("airbyte")


@fixture(name="test_config")
def config_fixture():
    return {
        "dataset": "dummy",
        "provider": {"bucket": "test-test", "endpoint": "test", "use_ssl": "test", "verify_ssl_cert": "test"},
        "path_pattern": "**",
        "format": {"delimiter": ","},
    }


@fixture(name="file_info")
def file_info_fixture():
    return FileInfo("dummyfile", 10, pendulum.now())


class MockFilesSource(AbstractFilesSource):
    @property
    def stream_class(self) -> type:
        return IncrementalFilesStream

    @property
    def spec_class(self) -> type:
        return FilesSpec

    @property
    def documentation_url(self) -> str:
        return "https://www.foo.bar"


# patching abstractmethods on IncrementalFileStream because the source methods instantiate the stream_class
@patch("airbyte_cdk.sources.streams.files.IncrementalFilesStream.__abstractmethods__", set())
class TestAbstractFilesSource:
    def test_read_config(self):
        with tempfile.NamedTemporaryFile("w+") as tmpfile:
            json.dump({"format": {"delimiter": "\\t"}}, tmpfile)
            tmpfile.seek(0)
            config = MockFilesSource().read_config(tmpfile.name)

        assert config["format"]["delimiter"] == "\t"

    def test_check_connection_exception(self, test_config):
        source = MockFilesSource()
        with patch.object(source.stream_class, "file_iterator", side_effect=Exception("couldn't connect")):
            passed, error_msg = source.check_connection(logger, config=test_config)
        assert not passed
        assert error_msg

    def test_check_connection_zero_files(self, test_config):
        source = MockFilesSource()
        with patch.object(source.stream_class, "file_iterator", MagicMock()):
            passed, error_msg = source.check_connection(logger, config=test_config)
        assert passed
        assert not error_msg

    def test_check_connection(self, test_config, file_info):
        source = MockFilesSource()
        with patch.object(source.stream_class, "file_iterator", MagicMock(return_value=[file_info])):
            passed, error_msg = source.check_connection(logger, config=test_config)
        assert passed
        assert not error_msg

    def test_streams(self, test_config):
        stream_list = MockFilesSource().streams(test_config)
        assert len(stream_list) == 1
        assert isinstance(stream_list[0], IncrementalFilesStream)

    def test_spec(self):
        source = MockFilesSource()
        with patch.object(source.spec_class, "schema", MagicMock()):
            spec = source.spec()
        assert isinstance(spec, ConnectorSpecification)
        assert spec.supportsIncremental  # this should be True since we're testing with IncrementalFilesStream
