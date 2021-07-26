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


import pytest

from airbyte_cdk.models import Type
from source_acceptance_test.base import BaseTest
from source_acceptance_test.utils import ConnectorRunner, full_refresh_only_catalog, serialize
from source_acceptance_test.utils.common import group_by_stream
from source_acceptance_test.utils.json_schema_helper import CatalogHelper


@pytest.mark.default_timeout(minutes=20)
class TestFullRefresh(BaseTest):
    def test_sequential_reads(self, connector_config, configured_catalog, docker_runner: ConnectorRunner):
        """Two sequential reads must produce identical result, but there are some exceptions:
        - new records added between reads (just ignored)
        - existing records updated between reads

        In both cases the test groups records by a stream and check if there PK defined, it can help identifying same records.
        If there is a PK then records can be different with only one condition - there must be cursor_field and it should also updated
        If there is no PK then records must be 100% equal.
        """
        configured_catalog = full_refresh_only_catalog(configured_catalog)
        output = docker_runner.call_read(connector_config, configured_catalog)
        records_1 = [message.record for message in output if message.type == Type.RECORD]

        output = docker_runner.call_read(connector_config, configured_catalog)
        records_2 = [message.record for message in output if message.type == Type.RECORD]

        helper = CatalogHelper(configured_catalog)
        records_1 = group_by_stream(records_1)
        records_2 = group_by_stream(records_2)
        empty_streams_after_2nd_read = set(records_1.keys()) - set(records_2.keys())
        assert not empty_streams_after_2nd_read, f"Second full refresh read has less streams with data: {empty_streams_after_2nd_read}"

        for stream_name in records_2.keys():
            stream = helper.stream(stream_name)
            if stream.primary_key:
                stream_records_1 = stream.group_by_keys(records_1[stream_name], stream.primary_key)
                stream_records_2 = stream.group_by_keys(records_2[stream_name], stream.primary_key)
                missing_pks = set(stream_records_1.keys()) - set(stream_records_2.keys())
                assert not missing_pks, f"There are records missing in second read of `{stream_name}` stream, PKs: {missing_pks}"

                cursor_field = stream.cursor_field
                for pk in stream_records_1.keys():
                    if stream_records_1[pk] == stream_records_2[pk]:
                        continue

                    if cursor_field:
                        cursor_fld_updated = cursor_field.parse(stream_records_1[pk]) < cursor_field.parse(stream_records_1[pk])
                        msg = f"The record (PK:{pk}) in {stream_name} stream changed between reads, but cursor_field remains less or equal"
                        assert cursor_fld_updated, msg
                    else:
                        msg = f"Cursor field is not defined for {stream_name} stream, so records should remains unchanged between reads"
                        assert stream_records_1[pk] == stream_records_2[pk], msg
            else:
                missing_records_after_2nd_read = set(map(serialize, records_1[stream_name])) - set(map(serialize, records_2[stream_name]))
                new_or_changed_records_after_2nd_read = set(map(serialize, records_2[stream_name])) - set(
                    map(serialize, records_1[stream_name])
                )
                msg = (
                    f"The following records changed between two reads in `{stream_name}` stream:\n{missing_records_after_2nd_read}\n"
                    f"New or changed records:\n{new_or_changed_records_after_2nd_read}\n"
                )
                assert not missing_records_after_2nd_read, msg
