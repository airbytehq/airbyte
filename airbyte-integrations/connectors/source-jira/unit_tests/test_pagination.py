#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
from http import HTTPStatus

import responses
from source_jira.streams import Projects
from source_jira.utils import read_full_refresh


@responses.activate
def test_pagination_projects():
    domain = "domain.com"
    responses_json = [
        (HTTPStatus.OK, {}, json.dumps({"startAt": 0, "maxResults": 2, "total": 6, "isLast": False, "values": [{"self": "p1"}, {"self": "p2"}]})),
        (HTTPStatus.OK, {}, json.dumps({"startAt": 2, "maxResults": 2, "total": 6, "isLast": False, "values": [{"self": "p3"}, {"self": "p4"}]})),
        (HTTPStatus.OK, {}, json.dumps({"startAt": 4, "maxResults": 2, "total": 6, "isLast": True, "values": [{"self": "p5"}, {"self": "p6"}]})),
    ]

    responses.add_callback(
        responses.GET,
        f"https://{domain}/rest/api/3/project/search",
        callback=lambda request: responses_json.pop(0),
        content_type="application/json",
    )

    stream = Projects(authenticator=None, domain=domain, projects=[])
    records = list(read_full_refresh(stream))
    assert records == [{"self": "p1"}, {"self": "p2"}, {"self": "p3"}, {"self": "p4"}, {"self": "p5"}, {"self": "p6"}]
