from unittest.mock import MagicMock

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode

from source_mixpanel.streams import Cohorts, Engage, CohortMembers

logger = AirbyteLogger()

MIXPANEL_BASE_URL = "https://mixpanel.com/api/2.0/"


def test_cohorts_stream_incremental(requests_mock):
    requests_mock.register_uri("GET", MIXPANEL_BASE_URL + "cohorts/list", setup_response(200, cohorts_response()))

    stream = Cohorts(authenticator=MagicMock())

    records = stream.read_records(
        sync_mode=SyncMode.incremental,
        stream_state={"created": "2019-04-02 23:22:01"})

    records_length = sum(1 for _ in records)
    assert records_length == 1


def test_engage_stream_incremental(requests_mock):
    requests_mock.register_uri("POST", MIXPANEL_BASE_URL + "engage?page_size=1000", setup_response(200, engage_response()))

    stream = Engage(authenticator=MagicMock())

    records = stream.read_records(
        sync_mode=SyncMode.incremental,
        cursor_field=["created"],
        stream_state={"created": "2008-12-12T11:20:47"})

    records_length = sum(1 for _ in records)
    assert records_length == 1


def test_cohort_members_stream_incremental(requests_mock):
    requests_mock.register_uri("POST", MIXPANEL_BASE_URL + "engage?page_size=1000", setup_response(200, engage_response()))
    requests_mock.register_uri("GET", MIXPANEL_BASE_URL + "cohorts/list", setup_response(200, cohorts_response))

    stream = CohortMembers(authenticator=MagicMock())

    records = stream.read_records(
        sync_mode=SyncMode.incremental,
        cursor_field=["created"],
        stream_state={"created": "2008-12-12T11:20:47"})

    records_length = sum(1 for _ in records)
    assert records_length == 1


def setup_response(status, body):
    return [
        {
            "json": body,
            "status_code": status
        }
    ]


def engage_response():
    return {
        "page": 0,
        "page_size": 1000,
        "session_id": "1234567890-EXAMPL",
        "status": "ok",
        "total": 2,
        "results": [
            {
                "$distinct_id": "9d35cd7f-3f06-4549-91bf-198ee58bb58a",
                "$properties": {
                    "$created": "2008-12-12T11:20:47",
                    "$browser": "Chrome",
                    "$browser_version": "83.0.4103.116",
                    "$email": "clark@asw.com",
                    "$first_name": "Clark",
                    "$last_name": "Kent",
                    "$name": "Clark Kent",
                }
            },
            {
                "$distinct_id": "cd9d357f-3f06-4549-91bf-158bb598ee8a",
                "$properties": {
                    "$created": "2008-11-12T11:20:47",
                    "$browser": "Firefox",
                    "$browser_version": "83.0.4103.116",
                    "$email": "bruce@asw.com",
                    "$first_name": "Bruce",
                    "$last_name": "Wayne",
                    "$name": "Bruce Wayne",
                }
            }
        ]
    }


def cohorts_response():
    return [
        {
            "count": 150,
            "is_visible": 1,
            "description": "This cohort is visible, has an id = 1000, and currently has 150 users.",
            "created": "2019-03-19 23:49:51",
            "project_id": 1,
            "id": 1000,
            "name": "Cohort One"
        },
        {
            "count": 25,
            "is_visible": 0,
            "description": "This cohort isn't visible, has an id = 2000, and currently has 25 users.",
            "created": "2019-04-02 23:22:01",
            "project_id": 1,
            "id": 2000,
            "name": "Cohort Two",
        }
    ]
