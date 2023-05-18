#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import pytest
from orchestrator.assets.specs_secrets_mask import get_secrets_properties_from_registry_entry


@pytest.mark.parametrize(
    "registry_entry, expected_secrets",
    [
        pytest.param(
            {
                "spec": {
                    "connectionSpecification": {
                        "properties": {
                            "azure_blob_storage_endpoint_domain_name": {"title": "Endpoint Domain Name", "type": "string"},
                            "azure_blob_storage_account_key": {
                                "title": "Azure Blob Storage account key",
                                "airbyte_secret": True,
                                "type": "string",
                            },
                            "azure_blob_storage_account_name": {
                                "title": "Azure Blob Storage account name",
                                "airbyte_secret": False,
                                "type": "string",
                            },
                        }
                    }
                }
            },
            ["azure_blob_storage_account_key"],
            id="Not nested properties with one secret",
        ),
        pytest.param(
            {
                "spec": {
                    "connectionSpecification": {
                        "properties": {
                            "azure_blob_storage_account_key": {
                                "title": "Azure Blob Storage account key",
                                "airbyte_secret": True,
                                "type": "string",
                            },
                            "nested_settings": {
                                "airbyte_secret": False,
                                "type": "object",
                                "properties": {
                                    "secret_nested_prop": {"airbyte_secret": True, "type": "string"},
                                    "not_secret_nested_prop": {"airbyte_secret": False, "type": "string"},
                                },
                            },
                        }
                    }
                }
            },
            ["azure_blob_storage_account_key", "secret_nested_prop"],
            id="Not nested properties with one secret",
        ),
    ],
)
def test_get_secrets_properties_from_registry_entry(registry_entry, expected_secrets):
    assert get_secrets_properties_from_registry_entry(registry_entry) == expected_secrets
