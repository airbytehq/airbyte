#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging

from .conftest import build_source


def test_oauth_and_service_account_scopes(manifest, base_config):
    """OAuth uses gmail.modify, while service-account JWT auth stays gmail.readonly.
    Workspace domain-wide delegation authorizes exact scope strings, so widening the JWT scope
    can cause existing connections to fail with unauthorized_client until admins re-authorize.
    """
    source = build_source(base_config)
    spec = source.spec(logging.getLogger(__name__))
    oauth_scopes = spec.advanced_auth.oauth_config_specification.oauth_connector_input_specification.scopes
    jwt_scope = manifest["definitions"]["jwt_authenticator"]["additional_jwt_payload"]["scope"]

    assert oauth_scopes == [{"scope": "https://www.googleapis.com/auth/gmail.modify"}]
    assert jwt_scope == "https://www.googleapis.com/auth/gmail.readonly"
