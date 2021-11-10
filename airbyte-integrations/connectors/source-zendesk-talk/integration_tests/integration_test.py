#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
from pathlib import Path

import pytest
from airbyte_protocol import ConfiguredAirbyteCatalog, Type
from base_python import AirbyteLogger
from source_zendesk_talk.source import SourceZendeskTalk

BASE_DIRECTORY = Path(__file__).resolve().parent.parent


@pytest.fixture(name="config_credentials")
def config_credentials_fixture():
    with open(str(BASE_DIRECTORY / "secrets/config.json"), "r") as f:
        return json.load(f)


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture():
    return ConfiguredAirbyteCatalog.parse_file(BASE_DIRECTORY / "sample_files/configured_catalog_activities_overview.json")


class TestZendeskTalkSource:
    def test_streams_outputs_records(self, config_credentials, configured_catalog):
        """
        Using standard tests is unreliable for Agent Activities and Agent Overview streams,
        because the data there changes in real-time, therefore additional pytests are used.
        """
        records = []
        for message in SourceZendeskTalk().read(AirbyteLogger(), config_credentials, configured_catalog):
            if message.type == Type.RECORD:
                records.append(message)

        assert len(records) > 0
