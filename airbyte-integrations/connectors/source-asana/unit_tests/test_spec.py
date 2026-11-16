# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.models import Type
from airbyte_cdk.test.entrypoint_wrapper import _run_command
from unit_tests.conftest import get_source


def test_oauth_spec() -> None:
    output = _run_command(get_source({}), ["spec"])
    assert not output.errors
    spec = output.get_message_by_types([Type.SPEC])[0].spec
    auth = spec.advanced_auth
    assert auth.auth_flow_type.value == "oauth2.0"
    assert auth.predicate_key == ["credentials", "option_title"]
    assert auth.predicate_value == "OAuth Credentials"
    oauth = auth.oauth_config_specification.oauth_connector_input_specification
    assert oauth.scopes == [{"scope": "default"}]
    assert oauth.access_token_url == "https://app.asana.com/-/oauth_token"
    assert oauth.extract_output == ["refresh_token"]
