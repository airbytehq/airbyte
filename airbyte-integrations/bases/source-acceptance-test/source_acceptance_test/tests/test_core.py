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


import json
from collections import Counter, defaultdict
from typing import List, MutableMapping, Mapping, Any

import pytest
from airbyte_protocol import ConnectorSpecification, Status, Type, AirbyteRecordMessage, AirbyteMessage
from docker.errors import ContainerError
from source_acceptance_test.base import BaseTest
from source_acceptance_test.config import BasicReadTestConfig, ConnectionTestConfig
from source_acceptance_test.utils import ConnectorRunner


@pytest.mark.timeout(10)
class TestSpec(BaseTest):
    def test_spec(self, connector_spec: ConnectorSpecification, docker_runner: ConnectorRunner):
        output = docker_runner.call_spec()
        spec_messages = [message for message in output if message.type == Type.SPEC]

        assert len(spec_messages) == 1, "Spec message should be emitted exactly once"
        if connector_spec:
            assert spec_messages[0].spec == connector_spec, "Spec should be equal to the one in spec.json file"


@pytest.mark.timeout(30)
class TestConnection(BaseTest):
    def test_check(self, connector_config, inputs: ConnectionTestConfig, docker_runner: ConnectorRunner):
        if inputs.status == ConnectionTestConfig.Status.Succeed:
            output = docker_runner.call_check(config=connector_config)
            con_messages = [message for message in output if message.type == Type.CONNECTION_STATUS]

            assert len(con_messages) == 1, "Connection status message should be emitted exactly once"
            assert con_messages[0].connectionStatus.status == Status.SUCCEEDED
        elif inputs.status == ConnectionTestConfig.Status.Failed:
            output = docker_runner.call_check(config=connector_config)
            con_messages = [message for message in output if message.type == Type.CONNECTION_STATUS]

            assert len(con_messages) == 1, "Connection status message should be emitted exactly once"
            assert con_messages[0].connectionStatus.status == Status.FAILED
        elif inputs.status == ConnectionTestConfig.Status.Exception:
            with pytest.raises(ContainerError) as err:
                docker_runner.call_check(config=connector_config)

            assert err.value.exit_status != 0, "Connector should exit with error code"
            assert "Traceback" in err.value.stderr.decode("utf-8"), "Connector should print exception"


@pytest.mark.timeout(30)
class TestDiscovery(BaseTest):
    def test_discover(self, connector_config, catalog, docker_runner: ConnectorRunner):
        output = docker_runner.call_discover(config=connector_config)
        catalog_messages = [message for message in output if message.type == Type.CATALOG]

        assert len(catalog_messages) == 1, "Catalog message should be emitted exactly once"
        if catalog:
            for stream1, stream2 in zip(catalog_messages[0].catalog.streams, catalog.streams):
                assert stream1.json_schema == stream2.json_schema, f"Streams: {stream1.name} vs {stream2.name}, stream schemas should match"
                stream1.json_schema = None
                stream2.json_schema = None
                assert stream1.dict() == stream2.dict(), f"Streams {stream1.name} and {stream2.name}, stream configs should match"


@pytest.mark.timeout(300)
class TestBasicRead(BaseTest):
    def test_read(self, connector_config, configured_catalog, inputs: BasicReadTestConfig, expected_records: List[AirbyteMessage],
                  docker_runner: ConnectorRunner):
        output = docker_runner.call_read(connector_config, configured_catalog)
        records = [message.record for message in output if message.type == Type.RECORD]
        counter = Counter(record.stream for record in records)

        all_streams = set(stream.stream.name for stream in configured_catalog.streams)
        streams_with_records = set(counter.keys())
        streams_without_records = all_streams - streams_with_records

        assert records, "At least one record should be read using provided catalog"

        if inputs.validate_output_from_all_streams:
            assert (
                not streams_without_records
            ), f"All streams should return some records, streams without records: {streams_without_records}"

        if expected_records:
            actual_by_stream = self.group_by_stream(records)
            expected_by_stream = self.group_by_stream(expected_records)
            for stream_name, expected in expected_by_stream.items():
                actual = actual_by_stream.get(stream_name, [])

                self.compare_records(
                    actual=actual, expected=expected,
                    extra_fields=inputs.expect_records.extra_fields,
                    exact_order=inputs.expect_records.exact_order,
                    extra_records=inputs.expect_records.extra_records,
                )

    @staticmethod
    def remove_extra_fields(record: Any, spec: Any) -> Any:
        """Remove keys from record that spec doesn't have, works recursively"""
        if not isinstance(spec, Mapping):
            return record

        assert isinstance(record, Mapping), "Record or part of it is not a dictionary, but expected record is."
        result = {}

        for k, v in spec.items():
            assert k in record, "Record or part of it doesn't have attribute that has expected record."
            result[k] = TestBasicRead.remove_extra_fields(record[k], v)

        return result

    @staticmethod
    def compare_records(actual, expected, extra_fields, exact_order, extra_records):
        """Compare records using combination of restrictions"""
        if exact_order:
            for r1, r2 in zip(expected, actual):
                if r1 is None:
                    assert extra_records, "There are more records than expected, but extra_records is off"
                    break
                if extra_fields:
                    r2 = TestBasicRead.remove_extra_fields(r2, r1)
                assert r1 == r2, "There mismatching in order of records or their values"
        else:
            expected = set(map(TestBasicRead.serialize_record_for_comparison, expected))
            actual = set(map(TestBasicRead.serialize_record_for_comparison, actual))
            missing_expected = set(expected) - set(actual)

            assert not missing_expected, "All expected records must be produced"

            if not extra_records:
                extra_actual = set(actual) - set(expected)
                assert not extra_actual, "There are more records than expected, but extra_records is off"

    @staticmethod
    def group_by_stream(records) -> MutableMapping[str, List[MutableMapping]]:
        """Group records by a source stream"""
        result = defaultdict(list)
        for record in records:
            result[record.stream].append(record.data)

        return result

    @staticmethod
    def serialize_record_for_comparison(record: Mapping) -> str:
        return json.dumps(record, sort_keys=True)
