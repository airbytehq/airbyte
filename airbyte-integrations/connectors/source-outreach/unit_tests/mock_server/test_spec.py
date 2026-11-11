# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import re
from unittest import TestCase

import yaml

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import _YAML_FILE_PATH

from .config import ConfigBuilder
from .request_builder import OutreachRequestBuilder
from .response_builder import page_response, resource
from .utils import given_token, read_stream, record_ids


_PROPERTIES = yaml.safe_load(_YAML_FILE_PATH.read_text())["spec"]["connection_specification"]["properties"]


class TestSpec(TestCase):
    def test_every_example_matches_its_pattern(self) -> None:
        checked = []
        for name, definition in _PROPERTIES.items():
            for example in definition.get("examples", []) if "pattern" in definition else []:
                checked.append(name)
                assert re.fullmatch(definition["pattern"], example), f"{name}: example {example!r} does not match its pattern"
        assert checked == ["start_date"]

    @HttpMocker()
    def test_read_accepts_the_num_workers_option(self, http_mocker: HttpMocker) -> None:
        given_token(http_mocker)
        http_mocker.get(
            OutreachRequestBuilder.endpoint("/users").build(),
            page_response([resource(1, "user", {"email": "rep@example.com", "updatedAt": "2024-01-02T03:04:05.000Z"})]),
        )

        output = read_stream("users", SyncMode.full_refresh, config=ConfigBuilder().with_num_workers(10).build())

        assert not output.errors
        assert record_ids(output) == [1]

    def test_read_rejects_fewer_than_two_workers(self) -> None:
        output = read_stream("users", SyncMode.full_refresh, config=ConfigBuilder().with_num_workers(1).build(), expecting_exception=True)

        assert output.records == []
        assert output.errors[0].trace.error.failure_type == FailureType.config_error
        assert "1 is less than the minimum of 2" in output.errors[0].trace.error.message
