#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
from source_google_ads.models import CustomerModel


@pytest.fixture(name="config")
def test_config():
    config = {
        "credentials": {
            "developer_token": "test_token",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "refresh_token": "test_refresh_token",
        },
        "customer_id": "123",
        "start_date": "2021-01-01",
        "conversion_window_days": 14,
        "custom_queries_array": [
            {
                "query": "SELECT campaign.accessible_bidding_strategy, segments.ad_destination_type, campaign.start_date, campaign.end_date FROM campaign",
                "primary_key": None,
                "cursor_field": "campaign.start_date",
                "table_name": "happytable",
            },
            {
                "query": "SELECT segments.ad_destination_type, segments.ad_network_type, segments.day_of_week, customer.auto_tagging_enabled, customer.id, metrics.conversions, campaign.start_date FROM campaign",
                "primary_key": "customer.id",
                "cursor_field": None,
                "table_name": "unhappytable",
            },
            {
                "query": "SELECT ad_group.targeting_setting.target_restrictions FROM ad_group",
                "primary_key": "customer.id",
                "cursor_field": None,
                "table_name": "ad_group_custom",
            },
        ],
    }
    return config


@pytest.fixture(autouse=True)
def mock_oauth_call(requests_mock):
    yield requests_mock.post(
        "https://accounts.google.com/o/oauth2/token",
        json={"access_token": "access_token", "refresh_token": "refresh_token", "expires_in": 0},
    )


@pytest.fixture
def customers(config):
    return [CustomerModel(id=_id, time_zone="local", is_manager_account=False) for _id in config["customer_id"].split(",")]

@pytest.fixture
def additional_customers(config, customers):
    return customers + [CustomerModel(id="789", time_zone="local", is_manager_account=False)]


@pytest.fixture
def customers_manager(config):
    return [CustomerModel(id=_id, time_zone="local", is_manager_account=True) for _id in config["customer_id"].split(",")]
