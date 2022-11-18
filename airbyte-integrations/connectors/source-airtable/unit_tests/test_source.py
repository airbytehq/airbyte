#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

from airbyte_cdk.models import AirbyteCatalog, ConnectorSpecification
from source_airtable.helpers import Helpers
from source_airtable.source import SourceAirtable


def test_spec(config):
    source = SourceAirtable()
    logger_mock = MagicMock()
    spec = source.spec(logger_mock)
    assert isinstance(spec, ConnectorSpecification)


def test_discover(config, mocker):
    source = SourceAirtable()
    logger_mock, Helpers.get_most_complete_row = MagicMock(), MagicMock()
    airbyte_catalog = source.discover(logger_mock, config)
    assert [stream.name for stream in airbyte_catalog.streams] == config["tables"]
    assert isinstance(airbyte_catalog, AirbyteCatalog)
    assert Helpers.get_most_complete_row.call_count == 2


@patch("requests.get")
def test_check_connection(config):
    source = SourceAirtable()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config) == (True, None)


def test_streams(config):
    source = SourceAirtable()
    Helpers.get_most_complete_row = MagicMock()
    streams = source.streams(config)
    assert len(streams) == 2
    assert [stream.name for stream in streams] == config["tables"]
