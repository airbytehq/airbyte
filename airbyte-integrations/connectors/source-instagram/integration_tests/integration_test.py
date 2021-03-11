"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
from pathlib import Path

from airbyte_protocol import ConfiguredAirbyteCatalog, Type
from base_python import AirbyteLogger
from source_instagram.source import SourceInstagram

BASE_DIRECTORY = Path(__file__).resolve().parent.parent
config = json.loads(open(f"{BASE_DIRECTORY}/secrets/config.json", "r").read())


class TestInstagramSource:
    # Using standard tests is unreliable for Inside streams, as the information for them may be updated.
    # It takes time to collect data on Insights, and during CI tests, a test for testIdenticalFullRefreshes is performed,
    # and during the execution of tests, a change in Insights may occur and we will not pass the tests.
    # Therefore, we use this test to test Insight streams.
    def test_insights_streams_outputs_records(self):
        catalog = self._read_catalog(f"{BASE_DIRECTORY}/sample_files/configured_catalog_insights.json")
        self._run_sync_test(config, catalog)

    @staticmethod
    def _read_catalog(path):
        return ConfiguredAirbyteCatalog.parse_raw(open(path, "r").read())

    @staticmethod
    def _run_sync_test(conf, catalog):
        records = []
        state = []
        for message in SourceInstagram().read(AirbyteLogger(), conf, catalog):
            if message.type == Type.RECORD:
                records.append(message)
            elif message.type == Type.STATE:
                state.append(message)

        assert len(records) > 0
        assert len(state) > 0
