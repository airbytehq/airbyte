####
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
####


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

import pytest
from airbyte_protocol import ConnectorSpecification, Status, Type
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
    def test_read(self, connector_config, configured_catalog, inputs: BasicReadTestConfig, docker_runner: ConnectorRunner):
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
