#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Dict

ZUORA_TENANT_ENDPOINT_MAP: Dict = {
    # Production
    "US Production": "https://rest.zuora.com",
    "US Cloud Production": "https://rest.na.zuora.com",
    "EU Production": "https://rest.eu.zuora.com",
    # Sandbox
    "US API Sandbox": "https://rest.apisandbox.zuora.com",
    "US Cloud API Sandbox": "https://rest.sandbox.na.zuora.com",
    "US Central Sandbox": "https://rest.test.zuora.com",
    "EU API Sandbox": "https://rest.sandbox.eu.zuora.com",
    "EU Central Sandbox": "https://rest.test.eu.zuora.com",
    # Performance Test
    "US Performance Test": "https://rest.pt1.zuora.com",
}


def get_url_base(tenant_endpoint: str) -> str:
    """Define the URL Base from user's input with respect to the ZUORA_TENANT_ENDPOINT_MAP"""
    return ZUORA_TENANT_ENDPOINT_MAP.get(tenant_endpoint)
