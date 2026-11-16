#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import pytest
from source_posthog import SourcePosthog

from airbyte_cdk.models import Status


def test_client_wrong_credentials(requests_mock):
    config = {"api_key": "blahblah", "start_date": "2021-01-01T00:00:00Z"}
    requests_mock.get("https://app.posthog.com/api/projects", status_code=401, json={"detail": "Invalid personal API key."})

    status = SourcePosthog(config=config).check(logger=logging.getLogger("airbyte"), config=config)

    assert status.status == Status.FAILED


@pytest.mark.parametrize(
    "detail, expected_message",
    [
        ("API key missing required scope: project:read", "API key is missing a required PostHog scope."),
        ("You do not have access to this project.", "Forbidden"),
        ("", "Forbidden"),
    ],
)
def test_forbidden_error_message(requests_mock, detail, expected_message):
    config = {"api_key": "api_key", "start_date": "2021-01-01T00:00:00Z"}
    requests_mock.get("https://app.posthog.com/api/projects", status_code=403, json={"detail": detail})

    status = SourcePosthog(config=config).check(logger=logging.getLogger("airbyte"), config=config)

    assert status.status == Status.FAILED
    assert expected_message in status.message
    if "missing required scope" not in detail:
        assert "API key is missing a required PostHog scope." not in status.message
