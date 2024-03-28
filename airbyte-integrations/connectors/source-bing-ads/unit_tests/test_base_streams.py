#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import patch

import pytest
import source_bing_ads
from source_bing_ads.base_streams import Accounts


@patch.object(source_bing_ads.source, "Client")
@pytest.mark.parametrize(
    "record, expected",
    [
        (
            {
                "AccountId": 16253412,
                "TaxCertificate": {
                    "TaxCertificates": {"KeyValuePairOfstringbase64Binary": [{"key": "test key", "value": "test value"}]},
                    "Status": "Active",
                    "TaxCertificateBlobContainerName": "Test Container Name",
                },
            },
            {
                "AccountId": 16253412,
                "TaxCertificate": {
                    "TaxCertificates": [{"key": "test key", "value": "test value"}],
                    "Status": "Active",
                    "TaxCertificateBlobContainerName": "Test Container Name",
                },
            },
        ),
        (
            {
                "AccountId": 16253412,
                "TaxCertificate": {
                    "TaxCertificates": [{"key": "test key", "value": "test value"}],
                    "Status": "Active",
                    "TaxCertificateBlobContainerName": "Test Container Name",
                },
            },
            {
                "AccountId": 16253412,
                "TaxCertificate": {
                    "TaxCertificates": [{"key": "test key", "value": "test value"}],
                    "Status": "Active",
                    "TaxCertificateBlobContainerName": "Test Container Name",
                },
            },
        ),
        (
            {
                "AccountId": 16253412,
            },
            {
                "AccountId": 16253412,
            },
        ),
        (
            {"AccountId": 16253412, "TaxCertificate": None},
            {"AccountId": 16253412, "TaxCertificate": None},
        ),
    ],
    ids=[
        "record_with_KeyValuePairOfstringbase64Binary_field",
        "record_without_KeyValuePairOfstringbase64Binary_field",
        "record_without_TaxCertificate_field",
        "record_with_TaxCertificate_is_None",
    ],
)
def test_accounts_transform_tax_fields(mocked_client, config, record, expected):
    stream = Accounts(mocked_client, config)
    actual = stream._transform_tax_fields(record)
    assert actual == expected
