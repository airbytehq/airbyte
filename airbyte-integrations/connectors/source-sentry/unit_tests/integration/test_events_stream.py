# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from config_builder import ConfigBuilder
from source_sentry.source import SourceSentry

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template
from airbyte_cdk.test.state_builder import StateBuilder


class TestEvents(TestCase):
    fr_read_file = "events_full_refresh"
    inc_read_file = "events_incremental"

    def catalog(self, sync_mode: SyncMode = SyncMode.full_refresh):
        return CatalogBuilder().with_stream(name="events", sync_mode=sync_mode).build()

    def config(self):
        return ConfigBuilder().build()

    def state(self):
        return StateBuilder().with_stream_state(stream_name="events", state={"dateCreated": "2023-01-01T00:00:00.0Z"}).build()

    @HttpMocker()
    def test_read(self, http_mocker: HttpMocker):
        http_mocker.get(
            HttpRequest(url="https://sentry.io/api/0/projects/test%20organization/test%20project/events/", query_params={"full": "true"}),
            HttpResponse(body=json.dumps(find_template(self.fr_read_file, __file__)), status_code=200),
        )
        config = self.config()
        catalog = self.catalog()
        source = SourceSentry(config=config, catalog=catalog, state=None)

        output = read(source=source, config=config, catalog=catalog)

        assert len(output.records) == 1

    @HttpMocker()
    def test_read_incremental(self, http_mocker: HttpMocker):
        http_mocker.get(
            HttpRequest(url="https://sentry.io/api/0/projects/test%20organization/test%20project/events/", query_params={"full": "true"}),
            HttpResponse(body=json.dumps(find_template(self.inc_read_file, __file__)), status_code=200),
        )
        config = self.config()
        catalog = self.catalog()
        state = self.state()
        source = SourceSentry(config=config, catalog=catalog, state=state)

        output = read(source=source, config=config, catalog=catalog, state=state)

        assert len(output.records) == 2
