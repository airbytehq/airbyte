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
from airbyte_protocol import Type
from standard_test import BaseTest
from standard_test.connector_runner import ConnectorRunner
from standard_test.utils import incremental_only_catalog


class TestIncremental(BaseTest):
    def test_sequential_reads(self, connector_config, configured_catalog, docker_runner: ConnectorRunner):
        configured_catalog = incremental_only_catalog(configured_catalog)
        output = docker_runner.call_read(connector_config, configured_catalog)

        records_1 = [message.record for message in output if message.type == Type.RECORD]
        states = [message.state for message in output if message.type == Type.STATE]

        assert states, "Should produce at least one state"

        latest_state = states[-1].data
        output = docker_runner.call_read_with_state(connector_config, configured_catalog, state=latest_state)

        records_2 = [message.record for message in output if message.type == Type.RECORD]
        states = [message.state for message in output if message.type == Type.STATE]

        assert records_1 == records_2, "TODO"
