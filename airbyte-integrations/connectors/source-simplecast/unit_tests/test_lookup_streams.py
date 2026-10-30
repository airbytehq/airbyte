import json
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {"api_token": "test_token"}
_CATEGORIES_REQUEST = HttpRequest("https://api.simplecast.com/categories")
_DISTRIBUTION_CHANNELS_REQUEST = HttpRequest("https://api.simplecast.com/distribution_channels")
_TIMEZONES_REQUEST = HttpRequest("https://api.simplecast.com/timezones")


def _read_stream(stream_name):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(get_source(config=_CONFIG), config=_CONFIG, catalog=catalog)
    assert output.errors == []
    return [record.record.data for record in output.records]


def _response(records):
    return HttpResponse(body=json.dumps({"collection": records}), status_code=200)


class LookupStreamsTest(TestCase):
    @HttpMocker()
    def test_categories_reads_the_full_lookup_once(self, http_mocker: HttpMocker):
        categories = [{"value": f"category-{i}"} for i in range(19)]
        http_mocker.get(_CATEGORIES_REQUEST, _response(categories))

        records = _read_stream("categories")

        assert len(records) == 19
        assert len({record["value"] for record in records}) == 19
        http_mocker.assert_number_of_calls(_CATEGORIES_REQUEST, 1)

    @HttpMocker()
    def test_distribution_channels_reads_the_full_lookup_once(self, http_mocker: HttpMocker):
        channels = [{"id": i, "name": f"channel-{i}"} for i in range(5)]
        http_mocker.get(_DISTRIBUTION_CHANNELS_REQUEST, _response(channels))

        records = _read_stream("distribution_channels")

        assert len(records) == 5
        assert len({record["id"] for record in records}) == 5
        http_mocker.assert_number_of_calls(_DISTRIBUTION_CHANNELS_REQUEST, 1)

    @HttpMocker()
    def test_timezones_reads_the_lookup_once(self, http_mocker: HttpMocker):
        timezones = [{"value": "Etc/UTC"}, {"value": "America/New_York"}]
        http_mocker.get(_TIMEZONES_REQUEST, _response(timezones))

        records = _read_stream("timezones")

        assert records == timezones
        http_mocker.assert_number_of_calls(_TIMEZONES_REQUEST, 1)
