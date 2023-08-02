#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
import requests
from source_confluence.source import Audit, BaseContentStream, BlogPosts, ConfluenceStream, Group, Pages, Space


class TestsConfluenceStream:
    confluence_stream_class = ConfluenceStream({"authenticator": MagicMock(), "domain_name": "test"})

    def tests_url_base(self):
        assert self.confluence_stream_class.url_base == "https://test/wiki/rest/api/"

    def test_primary_key(self):
        assert self.confluence_stream_class.primary_key == "id"

    def test_limit(self):
        assert self.confluence_stream_class.limit == 50

    def test_start(self):
        assert self.confluence_stream_class.start == 0

    def test_expand(self):
        assert self.confluence_stream_class.expand == []

    def test_next_page_token(self, requests_mock):
        url = "https://test.atlassian.net/wiki/rest/api/space"
        requests_mock.get(url, status_code=200, json={"_links": {"next": "test link"}})
        response = requests.get(url)
        assert self.confluence_stream_class.next_page_token(response=response) == {"start": 50}

    @pytest.mark.parametrize(
        ("stream_state", "stream_slice", "next_page_token", "expected"),
        [
            ({}, {}, {}, {'limit': 50, 'expand': ''}),
        ],
    )
    def test_request_params(self, stream_state, stream_slice, next_page_token, expected):
        assert self.confluence_stream_class.request_params(stream_state, stream_slice, next_page_token) == expected

    def test_parse_response(self, requests_mock):
        url = "https://test.atlassian.net/wiki/rest/api/space"
        requests_mock.get(url, status_code=200, json={"results": ["test", "test1", "test3"]})
        response = requests.get(url)
        assert list(self.confluence_stream_class.parse_response(response=response)) == ['test', 'test1', 'test3']


class TestBaseContentStream:
    base_content_stream_class = BaseContentStream({"authenticator": MagicMock(), "domain_name": "test"})

    def test_path(self):
        assert self.base_content_stream_class.path({}, {}, {}) == "content"

    def test_expand(self):
        assert self.base_content_stream_class.expand == ["history",
                                                         "history.lastUpdated",
                                                         "history.previousVersion",
                                                         "history.contributors",
                                                         "restrictions.read.restrictions.user",
                                                         "version",
                                                         "descendants.comment",
                                                         "body",
                                                         "body.storage",
                                                         "body.view",
                                                         ]

    def test_limit(self):
        assert self.base_content_stream_class.limit == 25

    def test_content_type(self):
        assert self.base_content_stream_class.content_type is None

    @pytest.mark.parametrize(
        ("stream_state", "stream_slice", "next_page_token", "expected"),
        [
            ({}, {}, {}, {'limit': 25,
                          'expand': 'history,history.lastUpdated,history.previousVersion,history.contributors,restrictions.'
                                    'read.restrictions.user,version,descendants.comment,body,body.storage,body.view',
                          'type': None}),
        ],
    )
    def test_request_params(self, stream_state, stream_slice, next_page_token, expected):
        assert self.base_content_stream_class.request_params(stream_state, stream_slice, next_page_token) == expected


class TestPages:
    pages_class = Pages({"authenticator": MagicMock(), "domain_name": "test"})

    def test_content_type(self):
        assert self.pages_class.content_type == "page"


class TestBlogPosts:
    blog_posts_class = BlogPosts({"authenticator": MagicMock(), "domain_name": "test"})

    def test_content_type(self):
        assert self.blog_posts_class.content_type == "blogpost"


class TestSpace:
    space_class = Space({"authenticator": MagicMock(), "domain_name": "test"})

    def test_api_name(self):
        assert self.space_class.api_name == "space"

    def test_expand(self):
        assert self.space_class.expand == ["permissions", "icon", "description.plain", "description.view"]


class TestGroup:
    group_class = Group({"authenticator": MagicMock(), "domain_name": "test"})

    def test_api_name(self):
        assert self.group_class.api_name == "group"


class TestAudit:
    audit_class = Audit({"authenticator": MagicMock(), "domain_name": "test"})

    def test_api_name(self):
        assert self.audit_class.api_name == "audit"

    def test_primary_key(self):
        assert self.audit_class.primary_key == "author"

    def test_limit(self):
        assert self.audit_class.limit == 1000
