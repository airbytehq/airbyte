# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the `report_webinars` stream (`acceptance-test-config.yml` `empty_streams`).

`GET /report/webinars/{webinarUUID}` for every webinar returned by `GET /users/{userId}/webinars`.
Keyed on the webinar `uuid` (double URL-encoded in the path), not paginated, the whole response body is
the record, injects `webinar_uuid`. A webinar with no report data (code 3001) is skipped.
"""

from unittest import TestCase

from airbyte_cdk.test.mock_http import HttpMocker

from .zoom_mocks import (
    ENCODED_UUIDS,
    WEBINAR_1,
    WEBINAR_2,
    WEBINARS,
    assert_completed_without_errors,
    assert_parent_400_is_skipped,
    assert_parent_403_fails_with_config_error,
    json_response,
    mock_webinar_parents,
    read_stream,
    records_data,
    request,
    zoom_error,
)


_STREAM = "report_webinars"
_REPORT_REQUESTS = {webinar["uuid"]: request(f"/report/webinars/{ENCODED_UUIDS[webinar['uuid']]}") for webinar in WEBINARS}


def _report(webinar):
    return {
        "id": webinar["id"],
        "uuid": webinar["uuid"],
        "topic": webinar["topic"],
        "duration": 60,
        "participants_count": 2,
        "start_time": "2026-01-01T10:00:00Z",
        "end_time": "2026-01-01T11:00:00Z",
    }


class TestReportWebinars(TestCase):
    @HttpMocker()
    def test_double_encodes_uuid_and_injects_webinar_uuid(self, http_mocker: HttpMocker):
        mock_webinar_parents(http_mocker)
        for webinar in WEBINARS:
            http_mocker.get(_REPORT_REQUESTS[webinar["uuid"]], json_response(_report(webinar)))

        output = read_stream(_STREAM)

        assert_completed_without_errors(output, _STREAM)
        assert sorted(records_data(output), key=lambda r: r["id"]) == [
            {**_report(webinar), "webinar_uuid": webinar["uuid"]} for webinar in WEBINARS
        ]
        for webinar in WEBINARS:
            http_mocker.assert_number_of_calls(_REPORT_REQUESTS[webinar["uuid"]], 1)

    @HttpMocker()
    def test_skips_webinar_without_report_3001(self, http_mocker: HttpMocker):
        mock_webinar_parents(http_mocker)
        http_mocker.get(_REPORT_REQUESTS[WEBINAR_1["uuid"]], json_response(_report(WEBINAR_1)))
        http_mocker.get(_REPORT_REQUESTS[WEBINAR_2["uuid"]], zoom_error(3001, "Meeting does not exist.", status_code=404))

        output = read_stream(_STREAM)

        assert_completed_without_errors(output, _STREAM)
        assert records_data(output) == [{**_report(WEBINAR_1), "webinar_uuid": WEBINAR_1["uuid"]}]
        assert output.is_in_logs("Zoom returned code 3001")

    def test_parent_400_yields_no_records(self):
        assert_parent_400_is_skipped(_STREAM)

    def test_parent_403_fails_with_config_error(self):
        assert_parent_403_fails_with_config_error(_STREAM)
