#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from pytest import fixture


@fixture
def config_pass():
    return {
        "authorization": {
            "auth_type": "Client",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "refresh_token": "test_refresh_token",
        },
        "start_date": "2022-01-01T00:00:00Z",
    }


@fixture
def auth_token():
    return {"access_token": "fake_access_token", "expires_in": 3600}


@fixture
def auth_url():
    return "https://api.rd.services/auth/token"


@fixture
def segmentations_url():
    return "https://api.rd.services/platform/segmentations"

@fixture
def analytics_conversions_url():
    return "https://api.rd.services/platform/analytics/conversions"

@fixture
def mock_segmentations_response():
    return {
        "segmentations": [
            {
                "id": 71625167165,
                "name": "A mock segmentation",
                "standard": True,
                "created_at": "2019-09-04T18:05:42.638-03:00",
                "updated_at": "2019-09-04T18:05:42.638-03:00",
                "process_status": "processed",
                "links": [
                    {
                        "rel": "SEGMENTATIONS.CONTACTS",
                        "href": "https://api.rd.services/platform/segmentations/71625167165/contacts",
                        "media": "application/json",
                        "type": "GET",
                    }
                ],
            }
        ]
    },
