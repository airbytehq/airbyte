#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

from airbyte_cdk.models import AirbyteCatalog, ConnectorSpecification
from source_airtable.source import SourceAirtable


def test_spec():
    source = SourceAirtable()
    logger_mock = MagicMock()
    spec = source.spec(logger_mock)
    assert isinstance(spec, ConnectorSpecification)


@patch("requests.get")
def test_discover(test_config):
    source = SourceAirtable()
    logger_mock = MagicMock()
    response = source.discover(logger_mock, test_config)
    assert isinstance(response, AirbyteCatalog)


@patch("requests.get")
def test_check_connection(test_config):
    source = SourceAirtable()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, test_config) == (True, None)


@patch("requests.get")
def test_streams(test_config):
    source = SourceAirtable()
    source.streams(test_config)
