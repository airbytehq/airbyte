# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http import HttpRequest


def nylas_request(path, query_params):
    return HttpRequest(
        url=f"https://api.us.nylas.com/v3/{path}",
        query_params=query_params,
        headers={"Authorization": "Bearer test-api-key"},
    )
