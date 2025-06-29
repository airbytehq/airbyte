#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
from http import HTTPStatus

import responses
from conftest import find_stream, read_full_refresh


@responses.activate
def test_pagination_users(config):
    domain = "domain.com"
    config["domain"] = domain
    responses_json = [
        (HTTPStatus.OK, {}, json.dumps([{"self": "user1"}, {"self": "user2"}])),
        (HTTPStatus.OK, {}, json.dumps([{"self": "user3"}, {"self": "user4"}])),
        (HTTPStatus.OK, {}, json.dumps([{"self": "user5"}])),
    ]

    responses.add_callback(
        responses.GET,
        f"https://{domain}/rest/api/3/users/search",
        callback=lambda request: responses_json.pop(0),
        content_type="application/json",
    )

    stream = find_stream("users", config)
    stream.retriever.paginator.pagination_strategy.page_size = 2
    records = list(read_full_refresh(stream))
    expected_records = [
        {"self": "user1"},
        {"self": "user2"},
        {"self": "user3"},
        {"self": "user4"},
        {"self": "user5"},
    ]

    for rec, exp in zip(records, expected_records):
        assert dict(rec) == exp, f"Failed at {rec} vs {exp}"
