#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import AirbyteCatalog
from source_airtable.source import SourceAirtable


@pytest.mark.parametrize(
    "status, check_passed",
    [
        (200, (True, None)),
        (401, (False, "Unauthorized. Please ensure you are authenticated correctly.")),
    ],
    ids=["success", "fail"],
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


def test_remove_missed_streams_from_catalog(mocker, config, fake_catalog, fake_streams, caplog):
    logger = logging.getLogger(__name__)
    source = SourceAirtable()
    mocker.patch("source_airtable.source.SourceAirtable.streams", return_value=fake_streams)
    streams_before = len(fake_catalog.streams)
    catalog = source._remove_missed_streams_from_catalog(logger=logger, config=config, catalog=fake_catalog)
    assert streams_before - len(catalog.streams) == 1
    assert len(caplog.messages) == 1
    assert caplog.text.startswith("WARNING")


#
