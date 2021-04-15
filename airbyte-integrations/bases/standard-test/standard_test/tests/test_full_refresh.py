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

import pytest
from airbyte_protocol import Type

from standard_test.base import BaseTest
from standard_test.connector_runner import ConnectorRunner
from standard_test.utils import full_refresh_only_catalog


@pytest.mark.timeout(300)
class TestFullRefresh(BaseTest):
    def test_sequential_reads(self, connector_config, configured_catalog, docker_runner: ConnectorRunner):
        configured_catalog = full_refresh_only_catalog(configured_catalog)
        output = docker_runner.call_read(connector_config, configured_catalog)
        records_1 = [message.record.data for message in output if message.type == Type.RECORD]

        output = docker_runner.call_read(connector_config, configured_catalog)
        records_2 = [message.record.data for message in output if message.type == Type.RECORD]

        assert not (
            set(map(json.dumps, records_1)) - set(map(json.dumps, records_2))
        ), "The two sequential reads should produce either equal set of records or one of them is a strict subset of the other"
