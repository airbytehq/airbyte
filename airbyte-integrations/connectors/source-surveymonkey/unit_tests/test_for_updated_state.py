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

import pendulum
import pytest
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from source_surveymonkey.streams import Surveys


class TestSurveymonkeySource:
    @staticmethod
    def get_stream():
        config = {"start_date": "2021-01-01T00:00:00", "access_token": "something"}
        authenticator = TokenAuthenticator(token=config["access_token"])
        start_date = pendulum.parse(config["start_date"])
        stream = Surveys(authenticator=authenticator, start_date=start_date)
        return stream

    @pytest.mark.parametrize(
        ("current_state", "lesser_date_record", "expected_state"),
        [
            (
                {"date_modified": "2021-06-10T11:02:01"},
                {"title": "test", "id": 100500, "date_modified": "2021-06-09T11:02:01"},
                {"date_modified": "2021-06-10T11:02:01"},
            ),
            (
                {"date_modified": "2021-06-10T11:02:01"},
                {"title": "test", "id": 100500, "date_modified": "2021-05-10T11:02:01"},
                {"date_modified": "2021-06-10T11:02:01"},
            ),
            (
                {"date_modified": "2021-06-10T11:02:01"},
                {"title": "test", "id": 100500, "date_modified": "2020-06-10T11:02:01"},
                {"date_modified": "2021-06-10T11:02:01"},
            ),
        ],
    )
    def test_get_updated_state_lesser(self, current_state, lesser_date_record, expected_state):
        stream = self.get_stream()
        # test lesser current state
        assert (
            stream.get_updated_state(current_state, lesser_date_record) == expected_state
        ), "the current state should not change if record cursor value is lesser than current"

    @pytest.mark.parametrize(
        ("current_state", "bigger_date_record", "expected_state"),
        [
            (
                {"date_modified": "2021-06-10T11:02:01"},
                {"title": "test", "id": 100500, "date_modified": "2021-06-10T11:02:02"},
                {"date_modified": "2021-06-10T11:02:02"},
            ),
            (
                {"date_modified": "2021-06-10T11:02:01"},
                {"title": "test", "id": 100500, "date_modified": "2025-06-10T11:02:01"},
                {"date_modified": "2025-06-10T11:02:01"},
            ),
            (
                {"date_modified": "2021-06-10T11:02:01"},
                {"title": "test", "id": 100500, "date_modified": "2021-08-10T11:02:01"},
                {"date_modified": "2021-08-10T11:02:01"},
            ),
        ],
    )
    def test_get_updated_state_bigger(self, current_state, bigger_date_record, expected_state):
        # test bigger current state
        stream = self.get_stream()
        assert (
            stream.get_updated_state(current_state, bigger_date_record) == expected_state
        ), "state should be updated when parsing newestly modified record"

    def test_get_updated_state_from_null_state(self):
        # test zero current state
        stream = self.get_stream()
        record_with_some_date = {"title": "test", "date_modified": "2000-06-15T18:09:00", "id": 1}
        expected_state = {stream.cursor_field: record_with_some_date[stream.cursor_field]}
        assert stream.get_updated_state({}, record_with_some_date) == expected_state
