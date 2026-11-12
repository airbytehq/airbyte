# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http import HttpRequest
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


class SimplecastRequestBuilder:
    @classmethod
    def collection(cls, stream_name, api_token):
        # These endpoints ignore all query parameters, including offset.
        return HttpRequest(
            url=f"https://api.simplecast.com/{stream_name}",
            query_params=ANY_QUERY_PARAMS,
            headers={"Authorization": f"Bearer {api_token}"},
        )
