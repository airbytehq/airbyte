# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import logging
from unittest.mock import MagicMock

import pytest
from source_google_ads import SourceGoogleAds

from airbyte_cdk.models import Status

from .conftest import Obj


CUSTOMER_CLIENT_RESPONSE = {
    "results": [
        {
            "customerClient": {
                "clientCustomer": "customers/1234567890",
                "manager": False,
                "status": "ENABLED",
                "id": "1234567890",
                "level": 0,
                "timeZone": "US/Eastern",
            }
        }
    ]
}
CUSTOMER_RESPONSE = {"results": [{"customer": {"id": "1234567890", "descriptiveName": "Test"}}]}
VALID_CUSTOM_QUERY_RESPONSE = {"results": [{"campaign": {"id": "456"}, "segments": {"date": "2021-01-08"}}]}
EMPTY_RESPONSE = {"results": []}


def _make_config(custom_queries_array):
    return {
        "credentials": {
            "developer_token": "test_token",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "refresh_token": "test_refresh_token",
        },
        "customer_id": "1234567890",
        "start_date": "2021-01-01",
        "conversion_window_days": 14,
        "custom_queries_array": custom_queries_array,
    }


def _mock_schema_loader(mocker, fields_metadata):
    query_object = MagicMock(return_value=fields_metadata)
    mocker.patch(
        "source_google_ads.components.CustomGAQuerySchemaLoader.google_ads_client",
        return_value=Obj(get_fields_metadata=query_object),
    )


def test_check_validates_valid_custom_query(requests_mock, mocker):
    """check succeeds when a custom GAQL query is valid and returns data."""
    config = _make_config(
        [
            {
                "query": "SELECT campaign.id, segments.date FROM campaign",
                "table_name": "test_valid_query",
            },
        ]
    )

    _mock_schema_loader(
        mocker,
        {
            "campaign.id": Obj(data_type=Obj(name="INT64"), is_repeated=False),
            "segments.date": Obj(data_type=Obj(name="DATE"), is_repeated=False),
        },
    )

    # OAuth token
    requests_mock.post(
        "https://www.googleapis.com/oauth2/v3/token",
        json={"access_token": "test", "expires_in": 3600},
    )
    # Accessible customers
    requests_mock.get(
        "https://googleads.googleapis.com/v20/customers:listAccessibleCustomers",
        json={"resourceNames": ["customers/1234567890"]},
    )
    # All searchStream calls share the same endpoint; responses are consumed in order
    requests_mock.post(
        "https://googleads.googleapis.com/v20/customers/1234567890/googleAds:searchStream",
        [
            {"json": CUSTOMER_CLIENT_RESPONSE},  # customer_client query (for customer stream)
            {"json": CUSTOMER_RESPONSE},  # customer stream check
            {"json": CUSTOMER_CLIENT_RESPONSE},  # customer_client query (for dynamic stream)
            {"json": VALID_CUSTOM_QUERY_RESPONSE},  # custom query check
            {"json": EMPTY_RESPONSE},
            {"json": EMPTY_RESPONSE},
        ],
    )

    source = SourceGoogleAds(None, config, None)
    result = source.check(logging.getLogger("test"), config)

    assert result.status == Status.SUCCEEDED


def test_check_fails_on_invalid_custom_query(requests_mock, mocker):
    """check fails when the API rejects the custom GAQL query with a 400 error."""
    config = _make_config(
        [
            {
                "query": "SELECT campaign.id, date, segments.date FROM campaign",
                "table_name": "test_invalid_query",
            },
        ]
    )

    _mock_schema_loader(
        mocker,
        {
            "campaign.id": Obj(data_type=Obj(name="INT64"), is_repeated=False),
            "date": Obj(data_type=Obj(name="DATE"), is_repeated=False),
            "segments.date": Obj(data_type=Obj(name="DATE"), is_repeated=False),
        },
    )

    requests_mock.post(
        "https://www.googleapis.com/oauth2/v3/token",
        json={"access_token": "test", "expires_in": 3600},
    )
    requests_mock.get(
        "https://googleads.googleapis.com/v20/customers:listAccessibleCustomers",
        json={"resourceNames": ["customers/1234567890"]},
    )
    requests_mock.post(
        "https://googleads.googleapis.com/v20/customers/1234567890/googleAds:searchStream",
        [
            {"json": CUSTOMER_CLIENT_RESPONSE},  # customer_client query (for customer stream)
            {"json": CUSTOMER_RESPONSE},  # customer stream check
            {"json": CUSTOMER_CLIENT_RESPONSE},  # customer_client query (for dynamic stream)
            {
                "json": {
                    "error": {
                        "code": 400,
                        "message": "Unrecognized field in the query: 'date'.",
                    }
                },
                "status_code": 400,
            },
            {"json": EMPTY_RESPONSE},
            {"json": EMPTY_RESPONSE},
        ],
    )

    source = SourceGoogleAds(None, config, None)
    result = source.check(logging.getLogger("test"), config)

    assert result.status == Status.FAILED


def test_check_succeeds_without_custom_queries(requests_mock):
    """check succeeds when no custom queries are configured."""
    config = _make_config([])

    requests_mock.post(
        "https://www.googleapis.com/oauth2/v3/token",
        json={"access_token": "test", "expires_in": 3600},
    )
    requests_mock.get(
        "https://googleads.googleapis.com/v20/customers:listAccessibleCustomers",
        json={"resourceNames": ["customers/1234567890"]},
    )
    requests_mock.post(
        "https://googleads.googleapis.com/v20/customers/1234567890/googleAds:searchStream",
        [
            {"json": CUSTOMER_CLIENT_RESPONSE},
            {"json": CUSTOMER_RESPONSE},
            {"json": EMPTY_RESPONSE},
            {"json": EMPTY_RESPONSE},
        ],
    )

    source = SourceGoogleAds(None, config, None)
    result = source.check(logging.getLogger("test"), config)

    assert result.status == Status.SUCCEEDED
