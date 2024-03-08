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
        return CatalogBuilder().with_stream(name="issues", sync_mode=sync_mode).build()

    def config(self):
        return ConfigBuilder().build()

    def state(self):
        return StateBuilder().with_stream_state(stream_name="issues", state={"lastSeen": "2023-01-01T00:00:00.0Z"}).build()

    @HttpMocker()
    def test_read(self, http_mocker: HttpMocker):
        response = [
          {
            "annotations": [],
            "assignedTo": None,
            "count": "1",
            "culprit": "raven.scripts.runner in main",
            "firstSeen": "2018-11-06T21:19:55Z",
            "hasSeen": False,
            "id": "1",
            "isBookmarked": False,
            "isPublic": False,
            "isSubscribed": True,
            "lastSeen": "2018-11-06T21:19:55Z",
            "level": "error",
            "logger": None,
            "metadata": {
              "title": "This is an example Python exception"
            },
            "numComments": 0,
            "permalink": "https://sentry.io/the-interstellar-jurisdiction/pump-station/issues/1/",
            "project": {
              "id": "2",
              "name": "Pump Station",
              "slug": "pump-station"
            },
            "shareId": None,
            "shortId": "PUMP-STATION-1",
            "stats": {
              "24h": [[1541455200, 473], [1541458800, 914], [1541462400, 991]]
            },
            "status": "unresolved",
            "statusDetails": {},
            "subscriptionDetails": None,
            "title": "This is an example Python exception",
            "type": "default",
            "userCount": 0
          }
        ]
        http_mocker.get(
            HttpRequest(
                url="https://sentry.io/api/0/projects/test%20organization/test%20project/issues/",
                query_params={"query": "lastSeen:>1900-01-01T00:00:00.0Z"}
            ),
            HttpResponse(body=json.dumps(response), status_code=200)

        )
        # https://sentry.io/api/1/projects/airbyte-09/airbyte-09/issues/?query=lastSeen%3A%3E2022-01-01T00%3A00%3A00.0Z
        output = read(SourceSentry(), self.config(), self.catalog())
        assert len(output.records) == 1

    @HttpMocker()
    def test_read_incremental(self, http_mocker: HttpMocker):
        response = [
            {
                "annotations": [],
                "assignedTo": None,
                "count": "1",
                "culprit": "raven.scripts.runner in main",
                "firstSeen": "2018-11-06T21:19:55Z",
                "hasSeen": False,
                "id": "1",
                "isBookmarked": False,
                "isPublic": False,
                "isSubscribed": True,
                "lastSeen": "2023-02-02T00:00:00.0Z",
                "level": "error",
                "logger": None,
                "metadata": {
                    "title": "This is an example Python exception"
                },
                "numComments": 0,
                "permalink": "https://sentry.io/the-interstellar-jurisdiction/pump-station/issues/1/",
                "project": {
                    "id": "2",
                    "name": "Pump Station",
                    "slug": "pump-station"
                },
                "shareId": None,
                "shortId": "PUMP-STATION-1",
                "stats": {
                    "24h": [[1541455200, 473], [1541458800, 914], [1541462400, 991]]
                },
                "status": "unresolved",
                "statusDetails": {},
                "subscriptionDetails": None,
                "title": "This is an example Python exception",
                "type": "default",
                "userCount": 0
            },
            {
                "annotations": [],
                "assignedTo": None,
                "count": "1",
                "culprit": "raven.scripts.runner in main",
                "firstSeen": "2018-11-06T21:19:55Z",
                "hasSeen": False,
                "id": "1",
                "isBookmarked": False,
                "isPublic": False,
                "isSubscribed": True,
                "lastSeen": "2023-01-02T00:00:00.0Z",
                "level": "error",
                "logger": None,
                "metadata": {
                    "title": "This is an example Python exception"
                },
                "numComments": 0,
                "permalink": "https://sentry.io/the-interstellar-jurisdiction/pump-station/issues/1/",
                "project": {
                    "id": "2",
                    "name": "Pump Station",
                    "slug": "pump-station"
                },
                "shareId": None,
                "shortId": "PUMP-STATION-1",
                "stats": {
                    "24h": [[1541455200, 473], [1541458800, 914], [1541462400, 991]]
                },
                "status": "unresolved",
                "statusDetails": {},
                "subscriptionDetails": None,
                "title": "This is an example Python exception",
                "type": "default",
                "userCount": 0
            }
        ]
        http_mocker.get(
            HttpRequest(
                url="https://sentry.io/api/0/projects/test%20organization/test%20project/issues/",
                query_params={"query": "lastSeen:>2023-01-01T00:00:00.0Z"}
            ),
            HttpResponse(body=json.dumps(response), status_code=200)

        )
        output = read(SourceSentry(), self.config(), self.catalog(SyncMode.incremental), self.state())
        assert len(output.records) == 2
