#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import json

import requests
from airbyte_cdk.sources.lcc.requesters.paginators.interpolated_paginator import InterpolatedPaginator
from airbyte_cdk.sources.lcc.requesters.paginators.next_page_url_paginator import NextPageUrlPaginator

config = {"option": "OPTION"}
response = requests.Response()
response.headers = {"A_HEADER": "HEADER_VALUE"}
response_body = {"_metadata": {"next": "https://airbyte.io/next_url"}}
response._content = json.dumps(response_body).encode("utf-8")
last_responses = [{"id": 0}]


def test_value_depends_response_body():
    next_page_tokens = {"next_page_url": "{{ decoded_response['_metadata']['next'] }}"}
    paginator = NextPageUrlPaginator("https://airbyte.io/", InterpolatedPaginator(next_page_tokens, config))

    next_page_token = paginator.next_page_token(response, last_responses)

    assert next_page_token == {"next_page_url": "next_url"}


def test_no_next_page_found():
    next_page_tokens = {"next_page_url": "{{ decoded_response['_metadata']['next'] }}"}
    paginator = NextPageUrlPaginator("https://airbyte.io/", InterpolatedPaginator(next_page_tokens, config))

    r = requests.Response()
    r._content = json.dumps({"data": []}).encode("utf-8")
    next_page_token = paginator.next_page_token(r, last_responses)

    assert next_page_token is None
