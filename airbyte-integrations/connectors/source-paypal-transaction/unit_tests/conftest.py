# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

# conftest.py
import json
from datetime import datetime
from unittest.mock import patch

import pytest
from source_paypal_transaction import SourcePaypalTransaction


@pytest.fixture(name="config")
def config_fixture():
    # From File test
    # with open('../secrets/config.json') as f:
    #     return json.load(f)
    # Mock test
    return {
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "start_date": "2024-01-30T00:00:00Z",
        "end_date": "2024-02-01T00:00:00Z",
        "dispute_start_date": "2024-02-01T00:00:00.000Z",
        "dispute_end_date": "2024-02-05T23:59:00.000Z",
        "buyer_username": "Your Buyer email",
        "buyer_password": "Your Buyer Password",
        "payer_id": "ypur ACCOUNT ID",
        "is_sandbox": True,
    }


@pytest.fixture(name="source")
def source_fixture():
    return SourcePaypalTransaction()


def validate_date_format(date_str, format):
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False


def test_date_formats_in_config(config):
    start_date_format = "%Y-%m-%dT%H:%M:%SZ"
    dispute_date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    assert validate_date_format(config["start_date"], start_date_format), "Start date format is incorrect"
    assert validate_date_format(config["end_date"], start_date_format), "End date format is incorrect"
    assert validate_date_format(config["dispute_start_date"], dispute_date_format), "Dispute start date format is incorrect"
    assert validate_date_format(config["dispute_end_date"], dispute_date_format), "Dispute end date format is incorrect"


@pytest.fixture(name="logger_mock")
def logger_mock_fixture():
    return patch("source_paypal_transactions.source.AirbyteLogger")
