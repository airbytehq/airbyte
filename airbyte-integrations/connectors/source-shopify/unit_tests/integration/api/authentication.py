# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.test.mock_http.response_builder import find_template
from source_shopify.scopes import SCOPES_MAPPING
from source_shopify.streams.base_streams import ShopifyStream

_ALL_SCOPES = [scope for stream_scopes in SCOPES_MAPPING.values() for scope in stream_scopes]


def set_up_shop(http_mocker: HttpMocker, shop_name: str) -> None:
    http_mocker.get(
        HttpRequest(f"https://{shop_name}.myshopify.com/admin/api/{ShopifyStream.api_version}/shop.json", query_params=ANY_QUERY_PARAMS),
        HttpResponse(json.dumps(find_template("shop", __file__)), status_code=200),
    )


def grant_all_scopes(http_mocker: HttpMocker, shop_name: str) -> None:
    http_mocker.get(
        HttpRequest(f"https://{shop_name}.myshopify.com/admin/oauth/access_scopes.json"),
        HttpResponse(json.dumps({"access_scopes": [{"handle": scope} for scope in _ALL_SCOPES]}), status_code=200),
    )
