# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the `webinar_registration_questions` stream (`acceptance-test-config.yml` `empty_streams`).

`GET /webinars/{webinarId}/registrants/questions` for every webinar returned by `GET /users/{userId}/webinars`.
Keyed on the webinar `id`, not paginated, the whole response body is the record, injects `webinar_id`.
A webinar deleted between listing and fetching (code 3001) is skipped.
"""

from unittest import TestCase

from airbyte_cdk.test.mock_http import HttpMocker

from .zoom_mocks import (
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


_STREAM = "webinar_registration_questions"
_QUESTIONS_REQUESTS = {webinar["id"]: request(f"/webinars/{webinar['id']}/registrants/questions") for webinar in WEBINARS}
_QUESTIONS_BODY = {
    "questions": [{"field_name": "job_title", "required": True}],
    "custom_questions": [{"title": "How did you hear about us?", "type": "short", "required": False, "answers": []}],
}


class TestWebinarRegistrationQuestions(TestCase):
    @HttpMocker()
    def test_reads_questions_for_every_webinar_and_injects_webinar_id(self, http_mocker: HttpMocker):
        mock_webinar_parents(http_mocker)
        for webinar in WEBINARS:
            http_mocker.get(_QUESTIONS_REQUESTS[webinar["id"]], json_response(_QUESTIONS_BODY))

        output = read_stream(_STREAM)

        assert_completed_without_errors(output, _STREAM)
        assert sorted(records_data(output), key=lambda r: r["webinar_id"]) == [
            {**_QUESTIONS_BODY, "webinar_id": webinar["id"]} for webinar in WEBINARS
        ]
        for webinar in WEBINARS:
            http_mocker.assert_number_of_calls(_QUESTIONS_REQUESTS[webinar["id"]], 1)

    @HttpMocker()
    def test_skips_deleted_webinar_3001(self, http_mocker: HttpMocker):
        # 404, not 400: this requester already ignores every 400.
        mock_webinar_parents(http_mocker)
        http_mocker.get(_QUESTIONS_REQUESTS[WEBINAR_1["id"]], json_response(_QUESTIONS_BODY))
        http_mocker.get(
            _QUESTIONS_REQUESTS[WEBINAR_2["id"]],
            zoom_error(3001, f"Webinar does not exist: {WEBINAR_2['id']}.", status_code=404),
        )

        output = read_stream(_STREAM)

        assert_completed_without_errors(output, _STREAM)
        assert [record["webinar_id"] for record in records_data(output)] == [WEBINAR_1["id"]]
        assert output.is_in_logs("Zoom returned code 3001")

    def test_parent_400_yields_no_records(self):
        assert_parent_400_is_skipped(_STREAM)

    def test_parent_403_fails_with_config_error(self):
        assert_parent_403_fails_with_config_error(_STREAM)
