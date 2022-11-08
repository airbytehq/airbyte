#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Dict

QONTO_ENDPOINT_MAP: Dict = {
    "Sandbox": "https://thirdparty-sandbox.staging.qonto.co/v2/",
    "Production": "https://thirdparty.qonto.com/v2/",
    "Test Mocked API Server": "https://stoplight.io/mocks/qonto-next/business-api/8419419/v2/",
}


def get_url_base(endpoint: str) -> str:
    """Define the URL Base from user's input with respect to the QONTO_ENDPOINT_MAP"""
    return QONTO_ENDPOINT_MAP.get(endpoint)
