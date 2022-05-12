#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.sources.cac.requesters.http_requester import HttpRequester


def test_kwargs():
    kwargs = {"url_base": "https://airbyte.io"}
    requester = HttpRequester(kwargs=kwargs)
    assert requester._url_base == "https://airbyte.io"
