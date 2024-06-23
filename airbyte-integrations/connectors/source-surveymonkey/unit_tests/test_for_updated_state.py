#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
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
        stream = Surveys(authenticator=authenticator, start_date=start_date, survey_ids=[])
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
            stream._get_updated_state(current_state, lesser_date_record) == expected_state
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
            stream._get_updated_state(current_state, bigger_date_record) == expected_state
        ), "state should be updated when parsing newestly modified record"

    def test_get_updated_state_from_null_state(self):
        # test zero current state
        stream = self.get_stream()
        record_with_some_date = {"title": "test", "date_modified": "2000-06-15T18:09:00", "id": 1}
        expected_state = {stream.cursor_field: record_with_some_date[stream.cursor_field]}
        assert stream._get_updated_state({}, record_with_some_date) == expected_state
