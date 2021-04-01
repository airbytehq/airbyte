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

from collections import Counter

from airbyte_protocol import Type, Status, ConnectorSpecification
from .utils import full_refresh_only_catalog, ConnectorRunner


class TestBaseInterface:
    def test_check(self, config, docker_runner: ConnectorRunner):
        output = docker_runner.call_check(config=config)
        con_messages = [message for message in output if message.type == Type.CONNECTION_STATUS]

        assert len(con_messages) == 1, "Connection status message should be emitted exactly once"
        assert con_messages[0].connectionStatus.status == Status.SUCCEEDED

    def test_discover(self, config, catalog, docker_runner: ConnectorRunner):
        output = docker_runner.call_discover(config=config)
        catalog_messages = [message for message in output if message.type == Type.CATALOG]

        assert len(catalog_messages) == 1, "Catalog message should be emitted exactly once"
        assert catalog_messages[0].catalog == catalog, "Catalog should match the one that was provided"

    def test_spec(self, spec_path, docker_runner: ConnectorRunner):
        output = docker_runner.call_spec()
        spec_messages = [message for message in output if message.type == Type.SPEC]

        spec = ConnectorSpecification.parse_file(spec_path)

        assert len(spec_messages) == 1, "Spec message should be emitted exactly once"
        # assert spec_messages[0].spec == spec, "Spec should be equal to the one in spec.json file"

    def test_read(self, config, configured_catalog, docker_runner: ConnectorRunner):
        configured_catalog = full_refresh_only_catalog(configured_catalog)
        output = docker_runner.call_read(config, configured_catalog)
        records = [message.record for message in output if message.type == Type.RECORD]
        counter = Counter(record.stream for record in records)

        all_streams = set(stream.stream.name for stream in configured_catalog.streams)
        streams_with_records = set(counter.keys())
        streams_without_records = all_streams - streams_with_records

        assert not streams_without_records, f"all streams should return some records, streams without records: {streams_without_records}"
