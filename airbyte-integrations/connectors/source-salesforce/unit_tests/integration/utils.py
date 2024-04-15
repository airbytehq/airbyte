# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from salesforce_describe_response_builder import SalesforceDescribeResponseBuilder


def given_stream(http_mocker: HttpMocker, base_url: str, stream_name: str, schema_builder: SalesforceDescribeResponseBuilder) -> None:
    http_mocker.get(
        HttpRequest(f"{base_url}/sobjects"),
        HttpResponse(json.dumps({"sobjects": [{"name": stream_name, "queryable": True}]})),
    )
    http_mocker.get(
        HttpRequest(f"{base_url}/sobjects/{stream_name}/describe"),
        schema_builder.build(),
    )
