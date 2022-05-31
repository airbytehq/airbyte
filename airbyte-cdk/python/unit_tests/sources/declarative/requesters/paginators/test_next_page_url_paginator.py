#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.requesters.paginators.interpolated_paginator import InterpolatedPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.next_page_url_paginator import NextPageUrlPaginator
from airbyte_cdk.sources.declarative.response import Response

config = {"option": "OPTION"}
headers = {"A_HEADER": "HEADER_VALUE"}
body = {"_metadata": {"next": "https://airbyte.io/next_url"}}
response = Response(headers=headers, body=body)

last_responses = [{"id": 0}]


def test_value_depends_response_body():
    next_page_tokens = {"next_page_url": "{{ decoded_response['_metadata']['next'] }}"}
    paginator = create_paginator(next_page_tokens)

    next_page_token = paginator.next_page_token(response, last_responses)

    assert next_page_token == {"next_page_url": "next_url"}


def test_no_next_page_found():
    next_page_tokens = {"next_page_url": "{{ decoded_response['_metadata']['next'] }}"}
    paginator = create_paginator(next_page_tokens)

    r = Response(body={"data": []})
    next_page_token = paginator.next_page_token(r, last_responses)

    assert next_page_token is None


def create_paginator(template):
    return NextPageUrlPaginator("https://airbyte.io/", InterpolatedPaginator(template, config))
