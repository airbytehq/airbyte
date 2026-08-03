#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
"""Unit tests for the source-reddit-ads OAuth authenticator token expiry handling.

Reddit's token endpoint (`https://www.reddit.com/api/v1/access_token`) returns
`expires_in` as a lifetime in seconds (RFC 6749 section 5.1), so the manifest must not
configure `token_expiry_date_format` -- doing so makes the CDK treat `expires_in` as an
absolute expiration timestamp, which parses `86400` as a 1970 epoch value and leaves the
token permanently expired (a token refresh before every API request). See
https://github.com/airbytehq/oncall/issues/13204 for context.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
from unittest.mock import patch

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now


MANIFEST_PATH = str(Path(__file__).resolve().parents[1] / "manifest.yaml")
CONFIG: Mapping[str, Any] = {
    "client_id": "test-client-id",
    "client_secret": "test-client-secret",
    "refresh_token": "test-refresh-token",
    "user_agent": "test:app:0.0.1 (by /u/tester)",
    "ad_account_id": "t2_testaccount",
    "start_time": "2024-05-11T00:00:00Z",
}
ONE_DAY_IN_SECONDS = 86400


@pytest.fixture(scope="module")
def authenticator() -> Any:
    source = YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=CONFIG)
    stream = next(s for s in source.streams(config=CONFIG) if s.name == "ad")
    partition = next(iter(stream.generate_partitions()))
    return partition._retriever.requester.authenticator


def test_expires_in_is_interpreted_as_seconds_until_expiry(authenticator: Any) -> None:
    """`expires_in` must be a duration, not an absolute timestamp."""
    assert authenticator.token_expiry_is_time_of_expiration is False
    assert authenticator.token_expiry_date_format is None


def test_parsed_expiry_lands_in_the_future(authenticator: Any) -> None:
    """A typical Reddit `expires_in` value must parse to roughly now + `expires_in` seconds."""
    before = ab_datetime_now()
    parsed = authenticator._parse_token_expiration_date(ONE_DAY_IN_SECONDS)
    delta = (parsed - before).total_seconds()
    assert ONE_DAY_IN_SECONDS - 60 < delta <= ONE_DAY_IN_SECONDS + 60, f"unexpected expiry {parsed}"


def test_token_is_not_expired_right_after_refresh(authenticator: Any) -> None:
    """After a refresh the token must be considered valid, otherwise every request refreshes it."""
    refresh_response = {
        "access_token": "new-access-token",
        "expires_in": ONE_DAY_IN_SECONDS,
        "refresh_token": "new-refresh-token",
    }
    with patch.object(type(authenticator), "_make_handled_request", return_value=refresh_response):
        authenticator.refresh_and_set_access_token()

    assert authenticator.token_has_expired() is False
    assert (authenticator.get_token_expiry_date() - ab_datetime_now()).total_seconds() > ONE_DAY_IN_SECONDS - 120
