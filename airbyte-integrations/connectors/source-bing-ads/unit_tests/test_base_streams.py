#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest

from conftest import find_stream


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
                "LastModifiedTime": "2025-01-01"
            },
            {
                "AccountId": 16253412,
                "TaxCertificate": {
                    "TaxCertificates": [{"key": "test key", "value": "test value"}],
                    "Status": "Active",
                    "TaxCertificateBlobContainerName": "Test Container Name",
                },
                "LastModifiedTime": "2025-01-01"
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
                "LastModifiedTime": "2025-01-01"
            },
            {
                "AccountId": 16253412,
                "TaxCertificate": {
                    "TaxCertificates": [{"key": "test key", "value": "test value"}],
                    "Status": "Active",
                    "TaxCertificateBlobContainerName": "Test Container Name",
                },
                "LastModifiedTime": "2025-01-01"
            },
        ),
        (
            {
                "AccountId": 16253412,
                "LastModifiedTime": "2025-01-01"
            },
            {
                "AccountId": 16253412,
                "LastModifiedTime": "2025-01-01"
            },
        ),
        (
            {
                "AccountId": 16253412,
                "TaxCertificate": None,
                "LastModifiedTime": "2025-01-01",
            },
            {
                "AccountId": 16253412,
                "TaxCertificate": None,
                "LastModifiedTime": "2025-01-01"
            },
        ),
    ],
    ids=[
        "record_with_KeyValuePairOfstringbase64Binary_field",
        "record_without_KeyValuePairOfstringbase64Binary_field",
        "record_without_TaxCertificate_field",
        "record_with_TaxCertificate_is_None",
    ],
)
def test_accounts_transform_tax_fields(config, record, expected):
    stream = find_stream("accounts", config)
    transformed_record = list(
        stream.retriever.record_selector.filter_and_transform(
            all_data=[record], stream_state={}, stream_slice={}, records_schema={}
        )
    )[0]
    if expected.get("TaxCertificate"):
        assert transformed_record["TaxCertificate"] == expected["TaxCertificate"]
    else:
        assert expected.get("TaxCertificate") is None
        assert transformed_record.get("TaxCertificate") is None
