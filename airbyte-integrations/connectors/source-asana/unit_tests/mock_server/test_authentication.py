# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import Type
from airbyte_cdk.test.entrypoint_wrapper import _run_command
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source
from unit_tests.mock_server.helpers import request, response


PAT = {"option_title": "PAT Credentials", "personal_access_token": "pat-token"}
OAUTH = {
    "option_title": "OAuth Credentials",
    "client_id": "client",
    "client_secret": "secret",
    "refresh_token": "refresh",
}


@pytest.mark.parametrize(
    "config,token,migrates",
    [
        ({"access_token": "legacy-token"}, "legacy-token", True),
        ({"credentials": PAT}, "pat-token", False),
        ({"credentials": OAUTH}, "oauth-token", False),
        ({"access_token": "stale", "credentials": PAT}, "pat-token", True),
        ({"access_token": "stale", "credentials": OAUTH}, "oauth-token", True),
        ({"access_token": "legacy-token", "credentials": {"personal_access_token": "legacy-token"}}, "legacy-token", True),
    ],
)
def test_check_authentication(config: dict, token: str, migrates: bool, tmp_path, capsys) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config))
    with HttpMocker() as http:
        if config.get("credentials", {}).get("option_title") == "OAuth Credentials":
            http.post(
                HttpRequest(
                    "https://app.asana.com/-/oauth_token",
                    body="grant_type=refresh_token&client_id=client&client_secret=secret&refresh_token=refresh",
                ),
                HttpResponse('{"access_token":"oauth-token","expires_in":3600}', 200),
            )
        workspaces = request("workspaces", token=token)
        http.get(workspaces, response())
        http.get(request("projects", token=token), response())
        source = get_source(config)
        emitted = [json.loads(line) for line in capsys.readouterr().out.splitlines() if line.startswith("{")]
        controls = [message for message in emitted if message.get("type") == "CONTROL"]
        output = _run_command(source, ["check", "--config", str(config_file)])
        assert not output.errors
        assert output.get_message_by_types([Type.CONNECTION_STATUS])[0].connectionStatus.status.value == "SUCCEEDED"
        http.assert_number_of_calls(workspaces, 1)
        assert len(controls) == int(migrates)
        if migrates:
            migrated = controls[0]["control"]["connectorConfig"]["config"]
            assert "access_token" not in migrated
            assert migrated["credentials"] == (
                config.get("credentials")
                if config.get("credentials", {}).get("option_title")
                else {"option_title": "PAT Credentials", "personal_access_token": token}
            )
