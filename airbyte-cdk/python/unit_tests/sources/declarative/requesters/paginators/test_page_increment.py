#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json

import requests
from airbyte_cdk.sources.declarative.requesters.paginators.page_increment import PageIncrement


def test_page_increment_paginator_strategy():
    paginator_strategy = PageIncrement()
    assert paginator_strategy._offset == 0

    response = requests.Response()

    response.headers = {"A_HEADER": "HEADER_VALUE"}
    response_body = {"next": "https://airbyte.io/next_url"}
    response._content = json.dumps(response_body).encode("utf-8")
    last_records = [{"id": 0}, {"id": 1}]

    paginator_strategy.next_page_token(response, last_records)
    assert paginator_strategy._offset == 1
    paginator_strategy.next_page_token(response, last_records)
    assert paginator_strategy._offset == 2
