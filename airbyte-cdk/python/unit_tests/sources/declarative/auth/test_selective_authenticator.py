#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.declarative.auth.selective_authenticator import SelectiveAuthenticator


def test_authenticator_selected(mocker):
    authenticators = {"one": mocker.Mock(), "two": mocker.Mock()}
    auth = SelectiveAuthenticator(
        config={"auth": {"type": "one"}},
        authenticators=authenticators,
        authenticator_selection_path=["auth", "type"],
    )

    assert auth is authenticators["one"]


def test_selection_path_not_found(mocker):
    authenticators = {"one": mocker.Mock(), "two": mocker.Mock()}

    with pytest.raises(ValueError, match="The path from `authenticator_selection_path` is not found in the config"):
        _ = SelectiveAuthenticator(
            config={"auth": {"type": "one"}},
            authenticators=authenticators,
            authenticator_selection_path=["auth_type"],
        )


def test_selected_auth_not_found(mocker):
    authenticators = {"one": mocker.Mock(), "two": mocker.Mock()}

    with pytest.raises(ValueError, match="The authenticator `unknown` is not found"):
        _ = SelectiveAuthenticator(
            config={"auth": {"type": "unknown"}},
            authenticators=authenticators,
            authenticator_selection_path=["auth", "type"],
        )
