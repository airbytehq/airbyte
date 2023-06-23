#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
from unittest import mock
from unittest.mock import patch

import pytest
import requests
from airbyte_cdk.entrypoint import launch
from unit_tests.sources.fixtures.source_test_fixture import (
    HttpTestStream,
    SourceFixtureOauthAuthenticator,
    SourceTestFixture,
    fixture_mock_send,
)


@pytest.mark.parametrize(
    "deployment_mode, url_base, expected_records, expected_error",
    [
        pytest.param("CLOUD", "https://airbyte.com/api/v1/", [], None, id="test_cloud_read_with_public_endpoint"),
        pytest.param("CLOUD", "http://unsecured.com/api/v1/", [], ValueError, id="test_cloud_read_with_unsecured_url"),
        pytest.param("CLOUD", "https://172.20.105.99/api/v1/", [], ValueError, id="test_cloud_read_with_private_endpoint"),
        pytest.param("CLOUD", "https://localhost:80/api/v1/", [], ValueError, id="test_cloud_read_with_localhost"),
        pytest.param("OSS", "https://airbyte.com/api/v1/", [], None, id="test_oss_read_with_public_endpoint"),
        pytest.param("OSS", "https://172.20.105.99/api/v1/", [], None, id="test_oss_read_with_private_endpoint"),
    ]
)
@patch.object(requests.Session, "send", fixture_mock_send)
def test_external_request_source(capsys, deployment_mode, url_base, expected_records, expected_error):
    source = SourceTestFixture()

    with mock.patch.dict(os.environ, {"DEPLOYMENT_MODE": deployment_mode}, clear=False):  # clear=True clears the existing os.environ dict
        with mock.patch.object(HttpTestStream, 'url_base', url_base):
            args = ['read', '--config', 'config.json', '--catalog', 'configured_catalog.json']
            if expected_error:
                with pytest.raises(expected_error):
                    launch(source, args)
            else:
                launch(source, args)


@pytest.mark.parametrize(
    "deployment_mode, token_refresh_url, expected_records, expected_error",
    [
        pytest.param("CLOUD", "https://airbyte.com/api/v1/", [], None, id="test_cloud_read_with_public_endpoint"),
        pytest.param("CLOUD", "http://unsecured.com/api/v1/", [], ValueError, id="test_cloud_read_with_unsecured_url"),
        pytest.param("CLOUD", "https://172.20.105.99/api/v1/", [], ValueError, id="test_cloud_read_with_private_endpoint"),
        pytest.param("OSS", "https://airbyte.com/api/v1/", [], None, id="test_oss_read_with_public_endpoint"),
        pytest.param("OSS", "https://172.20.105.99/api/v1/", [], None, id="test_oss_read_with_private_endpoint"),
    ]
)
@patch.object(requests.Session, "send", fixture_mock_send)
def test_external_oauth_request_source(deployment_mode, token_refresh_url, expected_records, expected_error):
    oauth_authenticator = SourceFixtureOauthAuthenticator(
        client_id="nora",
        client_secret="hae_sung",
        refresh_token="arthur",
        token_refresh_endpoint=token_refresh_url
    )
    source = SourceTestFixture(authenticator=oauth_authenticator)

    with mock.patch.dict(os.environ, {"DEPLOYMENT_MODE": deployment_mode}, clear=False):  # clear=True clears the existing os.environ dict
        args = ['read', '--config', 'config.json', '--catalog', 'configured_catalog.json']
        if expected_error:
            with pytest.raises(expected_error):
                launch(source, args)
        else:
            launch(source, args)
