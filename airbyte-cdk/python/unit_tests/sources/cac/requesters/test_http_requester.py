#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from unittest.mock import MagicMock

from airbyte_cdk.sources.cac.requesters.http_requester import HttpMethod, HttpRequester


def test():
    http_method = HttpMethod.GET

    request_parameters_provider = MagicMock()
    request_params = {"param": "value"}
    request_parameters_provider.request_params.return_value = request_params

    authenticator = MagicMock()

    config = {"url": "https://airbyte.io"}
    stream_slice = {"id": "1234"}

    requester = HttpRequester(
        url_base="{{ config['url'] }}",
        path="v1/{{ stream_slice['id'] }}",
        http_method=http_method,
        request_parameters_provider=request_parameters_provider,
        authenticator=authenticator,
        config=config,
    )

    assert requester.get_url_base() == "https://airbyte.io"
    assert requester.get_path(stream_state=None, stream_slice=stream_slice, next_page_token=None) == "v1/1234"
    assert requester.get_authenticator() == authenticator
    assert requester.get_method() == http_method
    assert requester.request_params(stream_state=None, stream_slice=None, next_page_token=None) == request_params
