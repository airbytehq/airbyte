# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock

import pytest
import requests
import requests_mock
from airbyte_cdk.sources.declarative.auth.token import BasicHttpAuthenticator, BearerAuthenticator
from source_zendesk_talk.components import IVRMenusRecordExtractor, IVRRoutesRecordExtractor, ZendeskTalkAuthenticator


@pytest.mark.parametrize(
    "response_data, expected_records",
    [
        # Test cases for IVRMenusRecordExtractor
        (
            {"ivrs": [{"id": "ivr_1", "menus": [{"id": "menu_1a", "name": "Menu 1A"}, {"id": "menu_1b", "name": "Menu 1B"}]}, {"id": "ivr_2", "menus": [{"id": "menu_2a", "name": "Menu 2A"}]}]},
            [{"ivr_id": "ivr_1", "id": "menu_1a", "name": "Menu 1A"}, {"ivr_id": "ivr_1", "id": "menu_1b", "name": "Menu 1B"}, {"ivr_id": "ivr_2", "id": "menu_2a", "name": "Menu 2A"}]
        ),
        ({"ivrs": []}, []),
        ({"ivrs": [{"id": "ivr_1", "menus": []}]}, []),
    ]
)
def test_ivr_menus_record_extractor(response_data, expected_records):
    with requests_mock.Mocker() as m:
        m.get('https://not-the-real.api/ivrs', json=response_data)
        response = requests.get('https://not-the-real.api/ivrs')

        extractor = IVRMenusRecordExtractor()
        records = extractor.extract_records(response)

        assert records == expected_records

@pytest.mark.parametrize(
    "response_data, expected_records",
    [
        # Test cases for IVRRoutesRecordExtractor
        (
            {"ivrs": [{"id": "ivr_1", "menus": [{"id": "menu_1a", "routes": [{"id": "route_1a1", "name": "Route 1A1"}, {"id": "route_1a2", "name": "Route 1A2"}]}]}]},
            [{"ivr_id": "ivr_1", "ivr_menu_id": "menu_1a", "id": "route_1a1", "name": "Route 1A1"}, {"ivr_id": "ivr_1", "ivr_menu_id": "menu_1a", "id": "route_1a2", "name": "Route 1A2"}]
        ),
        ({"ivrs": [{"id": "ivr_1", "menus": [{"id": "menu_1a", "routes": []}]}]}, []),
    ]
)
def test_ivr_routes_record_extractor(response_data, expected_records):
    with requests_mock.Mocker() as m:
        m.get('https://not-the-real.api/ivrs', json=response_data)
        response = requests.get('https://not-the-real.api/ivrs')

        extractor = IVRRoutesRecordExtractor()
        records = extractor.extract_records(response)

        assert records == expected_records

@pytest.mark.parametrize(
    "config, authenticator_type",
    [
        ({"access_token": "dummy_token", "email": "dummy@example.com"}, BasicHttpAuthenticator),
        ({"credentials": {"auth_type": "api_token"}}, BasicHttpAuthenticator),
        ({"credentials": {"auth_type": "oauth2.0"}}, BearerAuthenticator),
    ]
)
def test_zendesk_talk_authenticator(config, authenticator_type):
    legacy_basic_auth = MagicMock(spec=BasicHttpAuthenticator)
    basic_auth = MagicMock(spec=BasicHttpAuthenticator)
    oauth = MagicMock(spec=BearerAuthenticator)

    authenticator = ZendeskTalkAuthenticator(legacy_basic_auth, basic_auth, oauth, config)
    assert isinstance(authenticator, authenticator_type)

def test_zendesk_talk_authenticator_invalid():
    with pytest.raises(Exception) as excinfo:
        config = {"credentials": {"auth_type": "invalid"}}
        ZendeskTalkAuthenticator(None, None, None, config)
    assert "Missing valid authenticator" in str(excinfo.value)
