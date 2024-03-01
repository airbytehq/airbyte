import json
from unittest import TestCase

from airbyte_protocol.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.entrypoint_wrapper import read
from source_sentry.source import SourceSentry
from airbyte_cdk.test.state_builder import StateBuilder
from config_builder import ConfigBuilder


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
            HttpRequest("https://sentry.io/api/0/projects/test%20organization/test%20project/issues/"),
            HttpResponse(body=json.dumps(response), status_code=200)

        )
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
                "lastSeen": "2020-01-01T00:00:00.0Z",
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
            HttpRequest("https://sentry.io/api/0/projects/test%20organization/test%20project/issues/"),
            HttpResponse(body=json.dumps(response), status_code=200)

        )
        output = read(SourceSentry(), self.config(), self.catalog(SyncMode.incremental), self.state())
        assert len(output.records) == 1
