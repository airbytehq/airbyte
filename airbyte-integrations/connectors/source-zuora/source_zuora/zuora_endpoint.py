#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Dict

ZUORA_TENANT_ENDPOINT_MAP: Dict = {
    "US Production": "https://rest.zuora.com",
    "US API Sandbox": "https://rest.apisandbox.zuora.com",
    "US Performance Test": "https://rest.pt1.zuora.com",
    "US Cloud Production": "https://rest.na.zuora.com",
    "US Cloud API Sandbox": "https://rest.sandbox.na.zuora.com",
    "US Central Sandbox": "https://rest.test.zuora.com",
    "EU Production": "https://rest.eu.zuora.com",
    "EU API Sandbox": "https://rest.sandbox.eu.zuora.com",
    "EU Central Sandbox": "https://rest.test.eu.zuora.com",
}

def get_url_base(tenant_endpoint: str) -> str:
    """ Define the URL Base from user's input with respect to the ZUORA_TENANT_ENDPOINT_MAP """

    # map the tenant_type & endpoint from user's input
    tenant_type, endpoint = list(tenant_endpoint.items())[0]
    if tenant_type == "custom":
        # case with custom tenant URL should return the entered URL as url_base
        url_base = endpoint
    else:
        # all other cases should be handled by the tenant map
        url_base = ZUORA_TENANT_ENDPOINT_MAP.get(endpoint)
    return url_base