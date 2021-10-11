#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import pytest
import requests
from source_okta.source import OktaStream


class MockStream(OktaStream):
    primary_key = "None"

    def __init__(self):
        super().__init__("")

    def path(self, **kwargs) -> str:
        return "path"


class TestPagination:
    @pytest.mark.parametrize(
        ("_self_header", "_next_header", "expected_npt", "assert_msg"),
        [
            (None, "XYZ", {"after": "XYZ"}, "Expected to receive a new page token if next header is set and self is not set"),
            ("ABC", "XYZ", {"after": "XYZ"}, "Expected to receive a new page token if next and self headers have different values"),
            ("ABC", "ABC", None, "Expected no new page token if next and self headers are the same"),
            ("ABC", None, None, "Expected no new page token if next header is not set"),
        ],
    )
    def test_pagination(self, _self_header, _next_header, expected_npt, assert_msg):
        stream = MockStream()

        fake_response = requests.Response()
        link_header = ""

        if _self_header:
            link_header += f'<https://somedomain.com/api/v1/users?after={_self_header}>; rel="self",'

        if _next_header:
            link_header += f'<https://somedomain.com/api/v1/users?after={_next_header}>; rel="next"'

        fake_response.headers = {"link": link_header}

        actual_npt = stream.next_page_token(fake_response)

        assert actual_npt == expected_npt, assert_msg
