#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import requests
from airbyte_cdk.sources.lcc.requesters.paginators.offset_pagination import OffsetPagination

response = requests.Response()

tag = "cursor"
last_responses = [{"id": 0}, {"id": 1}]


def test_return_none_if_fewer_records_than_limit():
    limit = 5
    paginator = OffsetPagination(limit, tag)

    assert paginator._offset == 0

    next_page_token = paginator.next_page_token(response, last_responses)

    assert next_page_token is None


def test_return_next_offset_limit_1():
    limit = 1
    paginator = OffsetPagination(limit, tag)

    next_page_token = paginator.next_page_token(response, last_responses)

    assert next_page_token == {tag: 1}
    assert paginator._offset == 1


def test_return_next_offset_limit_2():
    limit = 2
    paginator = OffsetPagination(limit, tag)

    next_page_token = paginator.next_page_token(response, last_responses)

    assert next_page_token == {tag: 2}
    assert paginator._offset == 2

    next_page_token = paginator.next_page_token(response, [{"id": 2}])
    assert next_page_token is None
