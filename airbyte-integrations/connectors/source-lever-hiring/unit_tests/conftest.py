#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from pytest import fixture


@fixture
def config_pass():
    return {
        "credentials": {
            "auth_type": "Client",
            "client_id": "mock_client_id",
            "client_secret": "mock_client_secret",
            "refresh_token": "mock_refresh_token"
        },
        "environment": "Sandbox",
        "start_date": "2021-07-12T00:00:00Z"
    }


@fixture
def auth_token():
    return {"access_token": "good", "expires_in": 3600}


@fixture
def incremental_config_pass():
    return {
        "credentials": {
            "auth_type": "Client",
            "client_id": "mock_client_id",
            "client_secret": "mock_client_secret",
            "refresh_token": "mock_refresh_token"
        },
        "start_date": "2021-07-12T00:00:00Z",
        "environment": "Sandbox"
    }


@fixture
def opportunities_url():
    return "https://api.sandbox.lever.co/v1/opportunities"


@fixture
def auth_url():
    return "https://sandbox-lever.auth0.com/oauth/token"


@fixture
def users_url():
    return "https://api.sandbox.lever.co/v1/users"


@fixture
def mock_opportunities_response():
    return {
        "data": [
            {
                "id": "test_id",
                "name": "test_name",
                "contact": "test_contact",
                "headline": "test_headline",
                "stage": "test_stage",
                "confidentiality": "non-confidential",
                "location": "test_location",
                "phones": [{"type": "test_mobile", "value": "test_value"}],
                "emails": ["test_emails"],
                "links": ["test_link_1", "test_link_2"],
                "archived": {"reason": "test_reason", "archivedAt": 1628513942512},
                "tags": [],
                "sources": ["test_source_1"],
                "stageChanges": [{"toStageId": "test_lead-new", "toStageIndex": 0, "updatedAt": 1628509001183, "userId": "test_userId"}],
                "origin": "test_origin",
                "sourcedBy": "test_sourcedBy",
                "owner": "test_owner",
                "followers": ["test_follower"],
                "applications": ["test_application"],
                "createdAt": 1738509001183,
                "updatedAt": 1738542849132,
                "lastInteractionAt": 1738513942512,
                "lastAdvancedAt": 1738513942512,
                "snoozedUntil": None,
                "urls": {"list": "https://hire.sandbox.lever.co/candidates", "show": "https://hire.sandbox.lever.co/candidates/test_show"},
                "isAnonymized": False,
                "dataProtection": None,
            }
        ],
        "hasNext": False,
        "next": "%5B1628543173558%2C%227bf8c1ac-4a68-450f-bea0-a1e2c3f5aeaf%22%5D",
    }


@fixture
def mock_users_response():
    return {
        "data": [
            {
                "id": "fake_id",
                "name": "fake_name",
                "contact": "fake_contact",
                "headline": "Airbyte",
                "stage": "offer",
                "confidentiality": "non-confidential",
                "location": "Los Angeles, CA",
                "origin": "referred",
                "createdAt": 1628510997134,
                "updatedAt": 1628542848755,
                "isAnonymized": False,
            },
            {
                "id": "fake_id_2",
                "name": "fake_name_2",
                "contact": "fake_contact_2",
                "headline": "Airbyte",
                "stage": "applicant-new",
                "confidentiality": "non-confidential",
                "location": "Los Angeles, CA",
                "origin": "sourced",
                "createdAt": 1628509001183,
                "updatedAt": 1628542849132,
                "isAnonymized": False,
            },
        ],
        "hasNext": True,
        "next": "%5B1628543173558%2C%227bf8c1ac-4a68-450f-bea0-a1e2c3f5aeaf%22%5D",
    }

@fixture
def mock_users_response_no_next():
    return {
        "data": [
            {
                "id": "fake_id",
                "name": "fake_name",
                "contact": "fake_contact",
                "headline": "Airbyte",
                "stage": "offer",
                "confidentiality": "non-confidential",
                "location": "Los Angeles, CA",
                "origin": "referred",
                "createdAt": 1628510997134,
                "updatedAt": 1628542848755,
                "isAnonymized": False,
            },
        ],
        "hasNext": False,
    }
