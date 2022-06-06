#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import requests
from airbyte_cdk.sources.declarative.requesters.paginators.offset_paginator import OffsetPaginator
from airbyte_cdk.sources.declarative.states.dict_state import DictState

response = requests.Response()

tag = "cursor"
last_responses = [{"id": 0}, {"id": 1}]
state = DictState()


def test_return_none_if_fewer_records_than_limit():
    limit = 5
    paginator = OffsetPaginator(limit, state, tag)

    assert paginator._get_offset() == 0

    next_page_token = paginator.next_page_token(response, last_responses)

    assert next_page_token is None


def test_return_next_offset_limit_1():
    limit = 1
    paginator = OffsetPaginator(limit, state, tag)

    next_page_token = paginator.next_page_token(response, last_responses)

    assert next_page_token == {tag: 1}
    assert paginator._get_offset() == 1


def test_return_next_offset_limit_2():
    limit = 2
    paginator = OffsetPaginator(limit, state, tag)

    next_page_token = paginator.next_page_token(response, last_responses)

    assert next_page_token == {tag: 2}
    assert paginator._get_offset() == 2

    next_page_token = paginator.next_page_token(response, [{"id": 2}])
    assert next_page_token is None
