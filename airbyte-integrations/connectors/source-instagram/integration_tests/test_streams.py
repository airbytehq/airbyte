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
from collections import Counter
from typing import List, Tuple, Callable

import pytest
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog, Type
from source_instagram.source import SourceInstagram


@pytest.fixture(scope="session", name="config")
def config_fixture():
    with open("secrets/config.json", "r") as config_file:
        return json.load(config_file)


@pytest.fixture(scope="session", name="configured_catalog")
def configured_catalog_fixture():
    return ConfiguredAirbyteCatalog.parse_file("integration_tests/configured_catalog.json")


class TestFacebookMarketingSource:
    def test_insights_has_data(self, configured_catalog, config):
        catalog = self.slice_catalog(configured_catalog, lambda name: name.endswith("_insights"))
        records, states = self._read_records(config, catalog)

        counter = Counter(record.record.stream for record in records)
        for stream_name, rec_num in counter.items():
            assert rec_num, f"stream `{stream_name}` should have some records"

        assert records, "insights should produce states"

    @staticmethod
    def slice_catalog(catalog: ConfiguredAirbyteCatalog, predicate: Callable[[str], bool]) -> ConfiguredAirbyteCatalog:
        sliced_catalog = ConfiguredAirbyteCatalog(streams=[])
        for stream in catalog.streams:
            if predicate(stream.stream.name):
                sliced_catalog.streams.append(stream)
        return sliced_catalog

    @staticmethod
    def _read_records(conf, catalog, state=None) -> Tuple[List[AirbyteMessage], List[AirbyteMessage]]:
        records = []
        states = []
        for message in SourceInstagram().read(AirbyteLogger(), conf, catalog, state=state):
            if message.type == Type.RECORD:
                records.append(message)
            elif message.type == Type.STATE:
                states.append(message)

        return records, states
