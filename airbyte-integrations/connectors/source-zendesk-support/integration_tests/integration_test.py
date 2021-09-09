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

import pendulum
import requests_mock
from source_zendesk_support import SourceZendeskSupport
from source_zendesk_support.streams import Macros, TicketAudits, TicketMetrics, Tickets, Users

CONFIG_FILE = "secrets/config.json"


class TestIntegrationZendeskSupport:
    """This test class provides a set of tests for different Zendesk streams.
    The Zendesk API has difference pagination and sorting mechanisms for streams.
    Let's try to check them
    """

    @staticmethod
    def prepare_stream_args():
        """Generates streams settings from a file"""
        with open(CONFIG_FILE, "r") as f:
            return SourceZendeskSupport.convert_config2stream_args(json.loads(f.read()))

    def _test_export_stream(self, stream_cls: type):
        stream = stream_cls(**self.prepare_stream_args())
        stream.page_size = 1
        record_timestamps = {}
        for record in stream.read_records(sync_mode=None):
            # save the first 5 records
            if len(record_timestamps) > 5:
                break
            if stream._last_end_time not in record_timestamps.values():
                record_timestamps[record["id"]] = stream._last_end_time

        stream.page_size = 10
        for record_id, timestamp in record_timestamps.items():
            state = {"_last_end_time": timestamp}
            for record in stream.read_records(sync_mode=None, stream_state=state):
                assert record["id"] != record_id
                break

    def test_export_with_unixtime(self):
        """ Tickets stream has 'generated_timestamp' as cursor_field and it is unixtime format'' """
        self._test_export_stream(Tickets)

    def test_export_with_str_datetime(self):
        """ Other export streams has 'updated_at' as cursor_field and it is datetime  string format """
        self._test_export_stream(Users)

    def _test_insertion(self, stream_cls: type, index: int = None):
        """try to update some item"""
        stream = stream_cls(**self.prepare_stream_args())
        all_records = list(stream.read_records(sync_mode=None))
        state = stream.get_updated_state(current_stream_state=None, latest_record=all_records[-1])

        incremental_records = list(stream_cls(**self.prepare_stream_args()).read_records(sync_mode=None, stream_state=state))
        assert len(incremental_records) == 0

        if index is None:
            # select a middle index
            index = int(len(all_records) / 2)
        updated_record_id = all_records[index]["id"]
        all_records[index][stream.cursor_field] = stream.datetime2str(pendulum.now().astimezone())

        with requests_mock.Mocker() as m:
            url = stream.url_base + stream.path()
            data = {
                (stream.response_list_name or stream.name): all_records,
                "next_page": None,
            }
            m.get(url, text=json.dumps(data))
            incremental_records = list(stream_cls(**self.prepare_stream_args()).read_records(sync_mode=None, stream_state=state))

        assert len(incremental_records) == 1
        assert incremental_records[0]["id"] == updated_record_id

    def test_not_sorted_stream(self):
        """for streams without sorting but with pagination"""
        self._test_insertion(TicketMetrics)

    def test_sorted_page_stream(self):
        """for streams with pagination and sorting mechanism"""
        self._test_insertion(Macros, 0)

    def test_sorted_cursor_stream(self):
        """for stream with cursor pagination and sorting mechanism"""
        self._test_insertion(TicketAudits, 0)
