# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from contextlib import redirect_stdout
from io import StringIO
from typing import Any, Dict, List, Tuple
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker

from .config import ConfigBuilder
from .monday_requests import TeamsRequestBuilder
from .monday_requests.request_authenticators import ApiTokenAuthenticator
from .monday_responses import TeamsResponseBuilder
from .monday_responses.records import TeamsRecordBuilder
from .utils import read_stream


def _read_teams(config: Dict[str, Any]) -> Tuple[Any, List[Dict[str, Any]]]:
    # The config migration control message is printed to stdout by the source constructor, so it never
    # reaches the entrypoint output.
    stdout = StringIO()
    with redirect_stdout(stdout):
        output = read_stream("teams", SyncMode.full_refresh, config)
    control_messages = [json.loads(line) for line in stdout.getvalue().splitlines() if '"CONTROL"' in line]
    return output, control_messages


class TestLegacyApiTokenConfigMigration(TestCase):
    @HttpMocker()
    def test_given_legacy_config_when_read_then_migrate_to_credentials(self, http_mocker):
        http_mocker.post(
            TeamsRequestBuilder.teams_endpoint(ApiTokenAuthenticator("legacy-token")).build(),
            TeamsResponseBuilder.teams_response().with_record(TeamsRecordBuilder.teams_record()).build(),
        )

        output, control_messages = _read_teams({"api_token": "legacy-token"})

        assert len(output.records) == 1
        assert len(control_messages) == 1
        assert control_messages[0]["control"]["connectorConfig"]["config"] == {
            "api_token": "legacy-token",
            "credentials": {"api_token": "legacy-token", "auth_type": "api_token"},
        }

    @HttpMocker()
    def test_given_credentials_config_when_read_then_no_migration(self, http_mocker):
        http_mocker.post(
            TeamsRequestBuilder.teams_endpoint(ApiTokenAuthenticator("api-token")).build(),
            TeamsResponseBuilder.teams_response().with_record(TeamsRecordBuilder.teams_record()).build(),
        )

        output, control_messages = _read_teams(ConfigBuilder().with_api_token_credentials("api-token").build())

        assert len(output.records) == 1
        assert control_messages == []
