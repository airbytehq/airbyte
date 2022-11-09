#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from airbyte_cdk.sources.declarative.requesters.paginators.strategies.offset_increment import OffsetIncrement
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption
from source_prestashop.components import LimitOffsetPaginator


def test_limit_offset_paginator():
    limit_offset_option = RequestOption(inject_into="request_parameter", field_name="limit", options=None)
    pagination_strategy = OffsetIncrement(page_size=2, options=None)
    paginator = LimitOffsetPaginator(limit_offset_option=limit_offset_option, pagination_strategy=pagination_strategy, options=None)
    paginator.reset()
    assert paginator.get_request_params() == {"limit": "2"}
    next_page_token = paginator.next_page_token(response=MagicMock(), last_records=[{}, {}])
    assert next_page_token == {"next_page_token": 2}
    assert paginator.get_request_params() == {"limit": "2,2"}
    next_page_token = paginator.next_page_token(response=MagicMock(), last_records=[{}])
    assert next_page_token is None
