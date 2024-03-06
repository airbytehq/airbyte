# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_protocol.models import SyncMode
from config_builder import ConfigBuilder
from source_sentry.source import SourceSentry


class TestEvents(TestCase):
    def catalog(self, sync_mode: SyncMode = SyncMode.full_refresh):
        return CatalogBuilder().with_stream(name="events", sync_mode=sync_mode).build()

    def config(self):
        return ConfigBuilder().build()

    def state(self):
        return StateBuilder().with_stream_state(stream_name="events", state={"dateCreated": "2023-01-01T00:00:00.0Z"}).build()

    @HttpMocker()
    def test_read(self, http_mocker: HttpMocker):
        response = [
            {
                "eventID": "9fac2ceed9344f2bbfdd1fdacb0ed9b1",
                "tags": [
                    {"key": "browser", "value": "Chrome 60.0"},
                    {
                        "key": "device", "value": "Other"},
                    {"key": "environment", "value": "production"},
                    {"value": "fatal", "key": "level"},
                    {"key": "os", "value": "Mac OS X 10.12.6"},
                    {"value": "CPython 2.7.16", "key": "runtime"},
                    {"key": "release", "value": "17642328ead24b51867165985996d04b29310337"},
                    {"key": "server_name", "value": "web1.example.com"}
                ],
                "dateCreated": "2022-09-02T15:01:28.946777Z",
                "user": None,
                "message": "",
                "title": "This is an example Python exception",
                "id": "dfb1a2d057194e76a4186cc8a5271553",
                "platform": "python",
                "event.type": "error",
                "groupID": "1889724436"
            }
        ]
        http_mocker.get(
            HttpRequest(
                url="https://sentry.io/api/0/projects/test%20organization/test%20project/events/",
                query_params={"full": "true"}
            ),
            HttpResponse(body=json.dumps(response), status_code=200)

        )
        output = read(SourceSentry(), self.config(), self.catalog())
        assert len(output.records) == 1

    @HttpMocker()
    def test_read_incremental(self, http_mocker: HttpMocker):
        response = [
            {
                "eventID": "9fac2ceed9344f2bbfdd1fdacb0ed9b1",
                "tags": [
                    {"key": "browser", "value": "Chrome 60.0"},
                    {
                        "key": "device", "value": "Other"},
                    {"key": "environment", "value": "production"},
                    {"value": "fatal", "key": "level"},
                    {"key": "os", "value": "Mac OS X 10.12.6"},
                    {"value": "CPython 2.7.16", "key": "runtime"},
                    {"key": "release", "value": "17642328ead24b51867165985996d04b29310337"},
                    {"key": "server_name", "value": "web1.example.com"}
                ],
                "dateCreated": "2023-02-01T00:00:00.0Z",
                "user": None,
                "message": "",
                "title": "This is an example Python exception",
                "id": "dfb1a2d057194e76a4186cc8a5271553",
                "platform": "python",
                "event.type": "error",
                "groupID": "1889724436"
            },
            {
                "eventID": "9fac2ceed9344f2bbfdd1fdacb0ed9b1",
                "tags": [
                    {"key": "browser", "value": "Chrome 60.0"},
                    {
                        "key": "device", "value": "Other"},
                    {"key": "environment", "value": "production"},
                    {"value": "fatal", "key": "level"},
                    {"key": "os", "value": "Mac OS X 10.12.6"},
                    {"value": "CPython 2.7.16", "key": "runtime"},
                    {"key": "release", "value": "17642328ead24b51867165985996d04b29310337"},
                    {"key": "server_name", "value": "web1.example.com"}
                ],
                "dateCreated": "2024-01-02T15:01:28.946777Z",
                "user": None,
                "message": "",
                "title": "This is an example Python exception",
                "id": "dfb1a2d057194e76a4186cc8a5271553",
                "platform": "python",
                "event.type": "error",
                "groupID": "1889724436"
            }
        ]
        http_mocker.get(
            HttpRequest(
                url="https://sentry.io/api/0/projects/test%20organization/test%20project/events/",
                query_params={"full": "true"}
            ),
            HttpResponse(body=json.dumps(response), status_code=200)

        )
        output = read(SourceSentry(), self.config(), self.catalog(SyncMode.incremental), self.state())
        assert len(output.records) == 2
