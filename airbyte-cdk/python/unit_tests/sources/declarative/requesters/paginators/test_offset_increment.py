#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
from airbyte_cdk.sources.declarative.parsers.factory import DeclarativeComponentFactory
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.offset_increment import OffsetIncrement


@pytest.mark.parametrize(
    "test_name, page_size, options, expected_next_page_token, expected_offset",
    [
        ("test_same_page_size", "2", {}, 2, 2),
        ("test_same_page_size", 2, {}, 2, 2),
        ("test_larger_page_size", "{{ options['page_size'] }}", {"page_size": 3}, None, 0),
    ],
)
def test_offset_increment_paginator_strategy(test_name, page_size, options, expected_next_page_token, expected_offset):
    expected_type = DeclarativeComponentFactory.get_default_type("page_size", OffsetIncrement)
    page_size = expected_type(page_size)

    paginator_strategy = OffsetIncrement(page_size=page_size, options=options, config={})
    assert paginator_strategy._offset == 0

    response = requests.Response()

    response.headers = {"A_HEADER": "HEADER_VALUE"}
    response_body = {"next": "https://airbyte.io/next_url"}
    response._content = json.dumps(response_body).encode("utf-8")
    last_records = [{"id": 0}, {"id": 1}]

    next_page_token = paginator_strategy.next_page_token(response, last_records)
    assert expected_next_page_token == next_page_token
    assert expected_offset == paginator_strategy._offset

    paginator_strategy.reset()
    assert 0 == paginator_strategy._offset


def test_offset_increment_paginator_strategy_rises():
    paginator_strategy = OffsetIncrement(
        page_size="{{ options['page_size'] }}",
        options={"page_size": "invalid value"},
        config={}
    )
    with pytest.raises(Exception) as exc:
        paginator_strategy.get_page_size()
    assert str(exc.value) == 'invalid value is of type <class \'str\'>. Expected <class \'int\'>'
