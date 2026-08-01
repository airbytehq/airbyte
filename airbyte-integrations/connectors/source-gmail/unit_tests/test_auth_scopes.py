#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


def test_oauth_and_service_account_scopes(manifest):
    oauth_scopes = manifest["spec"]["advanced_auth"]["oauth_config_specification"]["oauth_connector_input_specification"]["scopes"]
    jwt_scope = manifest["definitions"]["jwt_authenticator"]["additional_jwt_payload"]["scope"]

    assert oauth_scopes == [{"scope": "https://www.googleapis.com/auth/gmail.modify"}]
    assert jwt_scope == "https://www.googleapis.com/auth/gmail.readonly"
