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
from standard_test.utils import filter_output, incremental_only_catalog


class TestIncremental(BaseTest):
    def test_sequential_reads(self, connector_config, configured_catalog, docker_runner: ConnectorRunner):
        configured_catalog = incremental_only_catalog(configured_catalog)
        output = docker_runner.call_read(connector_config, configured_catalog)

        records_1 = filter_output(output, type_=Type.RECORD)
        states_1 = filter_output(output, type_=Type.STATE)

        assert states_1, "The first incremental sync should produce at least one STATE message"
        assert records_1, "The first incremental sync should should produce at least one RECORD message"

        latest_state = states_1[-1].data
        output = docker_runner.call_read_with_state(connector_config, configured_catalog, state={})
        records_2 = filter_output(output, type_=Type.RECORD)
        states_2 = filter_output(output, type_=Type.STATE)

        assert states_1 == states_2, "Empty state should has same result as no state"
        assert records_1 == records_2, "Empty state should has same result as no state"

        output = docker_runner.call_read_with_state(connector_config, configured_catalog, state=latest_state)
        records_3 = filter_output(output, type_=Type.RECORD)
        states_3 = filter_output(output, type_=Type.STATE)

        assert not records_3, "There should be no records after second incremental read"
        assert states_1 == states_3, "State should not change if we pass the latest state"
