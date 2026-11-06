# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from _helpers import CONFIG, ORGANIZATION_URI, collection, list_request, read_stream, request, resource

from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse


def test_scheduled_events_reads_when_optional_lookback_days_is_omitted() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            request("users/me"), resource({"uri": "https://api.calendly.com/users/test-user", "current_organization": ORGANIZATION_URI})
        )
        events_request = list_request("scheduled_events")
        http_mocker.get(events_request, collection([]))

        output = read_stream("scheduled_events", CONFIG)

        assert not output.errors
        assert not output.records
        http_mocker.assert_number_of_calls(events_request, 1)


def test_rate_limit_retries_after_reset_header_seconds(recorded_sleeps: list[float]) -> None:
    user = {"uri": "https://api.calendly.com/users/test-user", "current_organization": ORGANIZATION_URI}
    with HttpMocker() as http_mocker:
        user_request = request("users/me")
        http_mocker.get(
            user_request,
            [
                HttpResponse(
                    body='{"title": "Too Many Requests"}',
                    status_code=429,
                    headers={"X-RateLimit-Reset": "60", "X-RateLimit-Remaining": "0"},
                ),
                resource(user),
            ],
        )

        output = read_stream("api_user", {**CONFIG, "lookback_days": 0})

        assert not output.errors
        assert [record.record.data for record in output.records] == [user]
        http_mocker.assert_number_of_calls(user_request, 2)
        assert any(60 <= seconds <= 61 for seconds in recorded_sleeps)
