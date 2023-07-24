#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus

import pytest


@pytest.fixture
def patch_base_class(mocker):
    assert True


def test_request_params(patch_base_class):
    assert True


def test_next_page_token(patch_base_class):
    assert True


def test_parse_response(patch_base_class):
    assert True


def test_request_headers(patch_base_class):
    assert True


def test_http_method(patch_base_class):
    assert True


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
    ],
)
def test_should_retry(patch_base_class, http_status, should_retry):
    assert True


def test_backoff_time(patch_base_class):
    assert True
