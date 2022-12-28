#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import AirbyteCatalog, ConnectorSpecification
from source_airtable.source import SourceAirtable


def test_spec(config):
    source = SourceAirtable()
    logger_mock = MagicMock()
    spec = source.spec(logger_mock)
    assert isinstance(spec, ConnectorSpecification)


@pytest.mark.parametrize(
    "status, check_passed",
    [
        (200, (True, None)),
        (401, (False, '401 Client Error: None for url: https://api.airtable.com/v0/meta/bases')),
    ],
    ids=["success", "fail"]
)
def test_check_connection(config, status, check_passed, fake_bases_response, fake_tables_response, requests_mock):
    source = SourceAirtable()
    # fake the bases
    requests_mock.get("https://api.airtable.com/v0/meta/bases", status_code=status, json=fake_bases_response)
    fake_base_id = fake_bases_response.get("bases")[0].get("id")
    # fake the tables based on faked bases
    requests_mock.get(f"https://api.airtable.com/v0/meta/bases/{fake_base_id}/tables", status_code=status, json=fake_tables_response)
    assert source.check_connection(MagicMock(), config) == check_passed


def test_discover(config, fake_bases_response, fake_tables_response, expected_discovery_stream_name, requests_mock):
    source = SourceAirtable()
    # fake the bases
    requests_mock.get("https://api.airtable.com/v0/meta/bases", status_code=200, json=fake_bases_response)
    fake_base_id = fake_bases_response.get("bases")[0].get("id")
    # fake the tables based on faked bases
    requests_mock.get(f"https://api.airtable.com/v0/meta/bases/{fake_base_id}/tables", status_code=200, json=fake_tables_response)
    # generate fake catalog
    airbyte_catalog = source.discover(MagicMock(), config)
    assert [stream.name for stream in airbyte_catalog.streams] == expected_discovery_stream_name
    assert isinstance(airbyte_catalog, AirbyteCatalog)


def test_streams(config, fake_bases_response, fake_tables_response, expected_discovery_stream_name, requests_mock):
    source = SourceAirtable()
    # fake the bases
    requests_mock.get("https://api.airtable.com/v0/meta/bases", status_code=200, json=fake_bases_response)
    fake_base_id = fake_bases_response.get("bases")[0].get("id")
    # fake the tables based on faked bases
    requests_mock.get(f"https://api.airtable.com/v0/meta/bases/{fake_base_id}/tables", status_code=200, json=fake_tables_response)
    streams = list(source.streams(config))
    assert len(streams) == 1
    assert [stream.name for stream in streams] == expected_discovery_stream_name

#
