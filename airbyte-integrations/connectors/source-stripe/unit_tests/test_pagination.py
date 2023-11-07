#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import random
from typing import Optional

import pytest
import requests
from airbyte_cdk.sources.declarative.requesters import RequestOption
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from source_stripe.source import StripePaginationStrategy, StripePaginator


@pytest.fixture
def initialize_paginator():
    def paginator_factory(page_size: Optional[int] = None) -> StripePaginator:
        page_size_request_option = RequestOption(inject_into=RequestOptionType.request_parameter, field_name="limit", parameters={})
        page_token_request_option = RequestOption(
            inject_into=RequestOptionType.request_parameter, field_name="starting_after", parameters={}
        )
        strategy = StripePaginationStrategy(page_size=page_size)
        return StripePaginator(
            page_size_option=page_size_request_option,
            page_token_option=page_token_request_option,
            pagination_strategy=strategy,
        )

    return paginator_factory


def test_paginator_with_pagination_strategy(initialize_paginator):
    page_size = 10
    last_records = [{"id": i, "title": f"Record {random.randint(1, 200)}"} for i in range(10)]

    paginator = initialize_paginator(page_size=page_size)

    response = requests.Response()
    response_body = {"data": last_records, "has_more": True}
    response._content = json.dumps(response_body).encode("utf-8")

    actual_request_params = paginator.get_request_params()
    actual_headers = paginator.get_request_headers()
    actual_body_data = paginator.get_request_body_data()
    actual_body_json = paginator.get_request_body_json()
    actual_next_page_token = paginator.next_page_token(response, last_records)
    assert actual_next_page_token == {"next_page_token": str(last_records[-1]["id"])}
    assert actual_request_params == {"limit": page_size}
    assert actual_headers == {}
    assert actual_body_data == {}
    assert actual_body_json == {}


def test_page_size_option_cannot_be_set_if_strategy_has_no_limit(initialize_paginator):
    with pytest.raises(ValueError):
        initialize_paginator()
        assert True


def test_reset(initialize_paginator):
    paginator = initialize_paginator(2)
    initial_request_parameters = paginator.get_request_params()

    last_records = [{"id": 5, "title": "Record 523"}, {"id": 6, "title": "Record 8273"}]
    response = requests.Response()
    response_body = {"_metadata": {"content": "content_value"}, "data": last_records, "has_more": True}
    response._content = json.dumps(response_body).encode("utf-8")

    paginator.next_page_token(response, last_records)

    request_parameters_for_second_request = paginator.get_request_params()
    paginator.reset()
    request_parameters_after_reset = paginator.get_request_params()
    assert initial_request_parameters == request_parameters_after_reset
    assert request_parameters_for_second_request != request_parameters_after_reset
