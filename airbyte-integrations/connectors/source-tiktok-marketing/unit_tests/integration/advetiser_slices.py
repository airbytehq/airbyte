# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


ADVERTISERS_FILE = "advertisers"


def mock_advertisers_slices(http_mocker: HttpMocker, config: dict):
    http_mocker.get(
        HttpRequest(
            url=f"https://business-api.tiktok.com/open_api/v1.3/oauth2/advertiser/get/",
            query_params={"secret": config["credentials"]["secret"], "app_id": config["credentials"]["app_id"]},
        ),
        HttpResponse(body=json.dumps(find_template(ADVERTISERS_FILE, __file__)), status_code=200),
    )
