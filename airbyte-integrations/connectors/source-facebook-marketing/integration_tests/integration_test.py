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

from airbyte_protocol import ConfiguredAirbyteCatalog, Type
from base_python import AirbyteLogger
from source_facebook_marketing.source import SourceFacebookMarketing

config = json.loads(open("secrets/config.json", "r").read())


class TestFacebookMarketingSource:
    def test_ad_insights_streams_outputs_records(self):
        catalog = self._read_catalog("sample_files/configured_catalog_adsinsights.json")
        self._run_sync_test(config, catalog)

    def test_ad_creatives_stream_outputs_records(self):
        catalog = self._read_catalog("sample_files/configured_catalog_adcreatives.json")
        self._run_sync_test(config, catalog)

    @staticmethod
    def _read_catalog(path):
        return ConfiguredAirbyteCatalog.parse_raw(open(path, "r").read())

    @staticmethod
    def _run_sync_test(conf, catalog):
        records = []
        state = []
        for message in SourceFacebookMarketing().read(AirbyteLogger(), conf, catalog):
            if message.type == Type.RECORD:
                records.append(message)
            elif message.type == Type.STATE:
                state.append(message)

        assert len(records) > 0
        assert len(state) > 0
