#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.streams import Stream
from pytest import fixture
from source_xero.source import SourceXero


@fixture(name="config_pass")
def config_fixture():
    return {
        "credentials": {
            "access_token": "goodone",
            "auth_type": "oauth2_access_token",
        },
        "tenant_id": "goodone",
        "start_date": "2021-01-01T00:00:00Z",
    }


@fixture(name="bad_config")
def bad_config_fixture():
    return {
        "credentials": {
            "access_token": "badone",
            "auth_type": "oauth2_access_token",
        },
        "start_date": "2021-01-01T00:00:00Z",
    }


@fixture(name="mock_bank_transaction_response")
def mock_bank_transactions():
    return {
        "BankTransactions": [
            {
                "BankTransactionID": "12345",
                "BankAccount": {"AccountID": "12345", "Name": "Business Account"},
                "Type": "SPEND",
                "Reference": "",
                "IsReconciled": False,
                "HasAttachments": False,
                "Contact": {
                    "ContactID": "12345",
                    "Name": "Paragorn",
                    "Addresses": [],
                    "Phones": [],
                    "ContactGroups": [],
                    "ContactPersons": [],
                    "HasValidationErrors": False,
                },
                "DateString": "2021-08-31T00:00:00",
                "Date": "/Date(1630368000000+0000)/",
                "Status": "AUTHORISED",
                "LineAmountTypes": "NoTax",
                "LineItems": [],
                "SubTotal": 3.00,
                "TotalTax": 0.00,
                "Total": 3.00,
                "UpdatedDateUTC": "/Date(1630412754013+0000)/",
                "CurrencyCode": "USD",
            }
        ]
    }


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> Stream:
    source = SourceXero()
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]
