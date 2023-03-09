#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
from http import HTTPStatus

import responses
from source_jira.streams import Issues, Projects, Users
from source_jira.utils import read_full_refresh


@responses.activate
def test_pagination_projects():
    domain = "domain.com"
    responses_json = [
        (HTTPStatus.OK, {}, json.dumps({"startAt": 0, "maxResults": 2, "total": 6, "isLast": False, "values": [{"id": "1"}, {"id": "2"}]})),
        (HTTPStatus.OK, {}, json.dumps({"startAt": 2, "maxResults": 2, "total": 6, "isLast": False, "values": [{"id": "3"}, {"id": "4"}]})),
        (HTTPStatus.OK, {}, json.dumps({"startAt": 4, "maxResults": 2, "total": 6, "isLast": True, "values": [{"id": "5"}, {"id": "6"}]})),
    ]

    responses.add_callback(
        responses.GET,
        f"https://{domain}/rest/api/3/project/search",
        callback=lambda request: responses_json.pop(0),
        content_type="application/json",
    )

    stream = Projects(authenticator=None, domain=domain, projects=[])
    records = list(read_full_refresh(stream))
    assert records == [{"id": "1"}, {"id": "2"}, {"id": "3"}, {"id": "4"}, {"id": "5"}, {"id": "6"}]


@responses.activate
def test_pagination_issues():
    domain = "domain.com"
    responses_json = [
        (HTTPStatus.OK, {}, json.dumps({"startAt": 0, "maxResults": 2, "total": 6, "issues": [{"id": "1", "updated": "2022-01-01"}, {"id": "2", "updated": "2022-01-01"}]})),
        (HTTPStatus.OK, {}, json.dumps({"startAt": 2, "maxResults": 2, "total": 6, "issues": [{"id": "3", "updated": "2022-01-01"}, {"id": "4", "updated": "2022-01-01"}]})),
        (HTTPStatus.OK, {}, json.dumps({"startAt": 4, "maxResults": 2, "total": 6, "issues": [{"id": "5", "updated": "2022-01-01"}, {"id": "6", "updated": "2022-01-01"}]})),
    ]

    responses.add_callback(
        responses.GET,
        f"https://{domain}/rest/api/3/search",
        callback=lambda request: responses_json.pop(0),
        content_type="application/json",
    )

    stream = Issues(authenticator=None, domain=domain, projects=[])
    stream.transform = lambda record, **kwargs: record
    records = list(read_full_refresh(stream))
    assert records == [
        {"id": "1", "updated": "2022-01-01"},
        {"id": "2", "updated": "2022-01-01"},
        {"id": "3", "updated": "2022-01-01"},
        {"id": "4", "updated": "2022-01-01"},
        {"id": "5", "updated": "2022-01-01"},
        {"id": "6", "updated": "2022-01-01"}
    ]


@responses.activate
def test_pagination_users():
    domain = "domain.com"
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

    stream = Users(authenticator=None, domain=domain, projects=[])
    stream.page_size = 2
    records = list(read_full_refresh(stream))
    assert records == [
        {"self": "user1"},
        {"self": "user2"},
        {"self": "user3"},
        {"self": "user4"},
        {"self": "user5"},
    ]
