#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
