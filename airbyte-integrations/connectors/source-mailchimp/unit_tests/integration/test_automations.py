# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
import datetime
import json
from unittest import TestCase

import freezegun
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template
from airbyte_cdk.test.state_builder import StateBuilder
from source_mailchimp import SourceMailchimp

from .config import ConfigBuilder

_CONFIG = ConfigBuilder().with_start_date(datetime.datetime(2023, 1, 1, 0, 0, 0, 1000)).build()


def _create_catalog(sync_mode: SyncMode = SyncMode.full_refresh):
    return CatalogBuilder().with_stream(name="automations", sync_mode=sync_mode).build()


@freezegun.freeze_time("2023-01-31T23:59:59.001000Z")
class AutomationsTest(TestCase):
    def setUp(self) -> None:
        """Base setup for all tests. Enter test mocker."""

        self.r_mock = HttpMocker()
        self.r_mock.__enter__()

    def teardown(self):
        """Stops and resets HttpMocker instance."""
        self.r_mock.__exit__()

    def test_read_full_refresh_no_pagination(self):
        """Ensure http integration and record extraction"""
        self.r_mock.get(
            HttpRequest(
                url="https://us10.api.mailchimp.com/3.0/automations",
                query_params={
                    "sort_field": "create_time",
                    "sort_dir": "ASC",
                    "exclude_fields": "automations._links",
                    "count": 1000,
                    "since_create_time": "2022-12-31T23:59:59.001000Z",
                    "before_create_time": "2023-01-31T23:59:59.001000Z",
                },
            ),
            HttpResponse(json.dumps(find_template("automations", __file__)), 200),
        )

        source = SourceMailchimp()
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert len(actual_messages.records) == 1

    def test_full_refresh_with_pagination(self):
        """Ensure pagination"""
        self.r_mock.get(
            HttpRequest(
                url="https://us10.api.mailchimp.com/3.0/automations",
                query_params={
                    "sort_field": "create_time",
                    "sort_dir": "ASC",
                    "exclude_fields": "automations._links",
                    "count": 1000,
                    "since_create_time": "2022-12-31T23:59:59.001000Z",
                    "before_create_time": "2023-01-31T23:59:59.001000Z",
                },
            ),
            HttpResponse(json.dumps({"automations": find_template("automations", __file__)["automations"] * 1002}), 200),
        )
        self.r_mock.get(
            HttpRequest(
                url="https://us10.api.mailchimp.com/3.0/automations",
                query_params={
                    "sort_field": "create_time",
                    "sort_dir": "ASC",
                    "exclude_fields": "automations._links",
                    "count": 1000,
                    "offset": 1002,
                    "since_create_time": "2022-12-31T23:59:59.001000Z",
                    "before_create_time": "2023-01-31T23:59:59.001000Z",
                },
            ),
            HttpResponse(json.dumps(find_template("automations", __file__)), 200),
        )
        source = SourceMailchimp()
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert len(actual_messages.records) == 1003

    def test_when_read_incrementally_then_emit_state_message(self):
        """Ensure incremental sync emits correct stream state message"""

        self.r_mock.get(
            HttpRequest(
                url="https://us10.api.mailchimp.com/3.0/automations",
                query_params={
                    "sort_field": "create_time",
                    "sort_dir": "ASC",
                    "exclude_fields": "automations._links",
                    "count": 1000,
                    "since_create_time": "2022-12-31T23:59:59.001000Z",
                    "before_create_time": "2023-01-31T23:59:59.001000Z",
                },
            ),
            HttpResponse(json.dumps(find_template("automations", __file__)), 200),
        )

        source = SourceMailchimp()
        actual_messages = read(
            source,
            config=_CONFIG,
            catalog=_create_catalog(sync_mode=SyncMode.incremental),
            state=StateBuilder().with_stream_state("automations", {"create_time": "2220-11-23T05:42:11+00:00"}).build(),
        )
        actual_messages.state_messages[0].state.stream.stream_state == {"create_time": "2220-11-23T05:42:11+00:00"}
