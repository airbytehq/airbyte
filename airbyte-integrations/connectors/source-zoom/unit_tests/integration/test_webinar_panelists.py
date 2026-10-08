# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the `webinar_panelists` stream (`acceptance-test-config.yml` `empty_streams`).

`GET /webinars/{webinarId}/panelists` for every webinar returned by `GET /users/{userId}/webinars`.
Keyed on the webinar `id`, not paginated, records under `panelists`, injects `webinar_id`.
"""

from unittest import TestCase

from airbyte_cdk.test.mock_http import HttpMocker

from .zoom_mocks import (
    WEBINARS,
    assert_completed_without_errors,
    assert_parent_400_is_skipped,
    assert_parent_403_fails_with_config_error,
    json_response,
    mock_webinar_parents,
    read_stream,
    records_data,
    request,
)


_STREAM = "webinar_panelists"


_PANELISTS_REQUESTS = {webinar["id"]: request(f"/webinars/{webinar['id']}/panelists") for webinar in WEBINARS}


class TestWebinarPanelists(TestCase):
    @HttpMocker()
    def test_reads_panelists_for_every_webinar_and_injects_webinar_id(self, http_mocker: HttpMocker):
        mock_webinar_parents(http_mocker)
        for webinar in WEBINARS:
            http_mocker.get(
                _PANELISTS_REQUESTS[webinar["id"]],
                json_response(
                    {
                        "total_records": 1,
                        "panelists": [{"id": f"p-{webinar['id']}", "email": f"{webinar['id']}@example.com", "name": "Panelist"}],
                    }
                ),
            )

        output = read_stream(_STREAM)

        assert_completed_without_errors(output, _STREAM)
        assert sorted(records_data(output), key=lambda r: r["id"]) == [
            {"id": f"p-{webinar['id']}", "email": f"{webinar['id']}@example.com", "name": "Panelist", "webinar_id": webinar["id"]}
            for webinar in WEBINARS
        ]
        for webinar in WEBINARS:
            http_mocker.assert_number_of_calls(_PANELISTS_REQUESTS[webinar["id"]], 1)

    def test_parent_400_yields_no_records(self):
        assert_parent_400_is_skipped(_STREAM)

    def test_parent_403_fails_with_config_error(self):
        assert_parent_403_fails_with_config_error(_STREAM)
