from unittest.mock import MagicMock

import pytest
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode

from source_mixpanel.source import (
    MixpanelStream,
    IncrementalMixpanelStream,
    FunnelsList,
    EngageSchema,
    Annotations,
    Revenue,
    Funnels,
    ExportSchema,
    Export
)

logger = AirbyteLogger()

MIXPANEL_BASE_URL = "https://mixpanel.com/api/2.0/"

MIXPANEL_DATA_BASE_URL = "https://data.mixpanel.com/api/2.0/"


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(MixpanelStream, "path", "v0/example_endpoint")
    mocker.patch.object(MixpanelStream, "primary_key", "test_primary_key")
    mocker.patch.object(MixpanelStream, "__abstractmethods__", set())


@pytest.fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalMixpanelStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalMixpanelStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalMixpanelStream, "cursor_field", "date")
    mocker.patch.object(IncrementalMixpanelStream, "__abstractmethods__", set())


def test_url_base(patch_base_class):
    stream = MixpanelStream(authenticator=MagicMock())

    assert stream.url_base == "https://mixpanel.com/api/2.0/"


def test_request_headers(patch_base_class):
    stream = MixpanelStream(authenticator=MagicMock())

    assert stream.request_headers(stream_state={}) == {"Accept": "application/json"}


def test_updated_state(patch_incremental_base_class):
    stream = IncrementalMixpanelStream(authenticator=MagicMock())

    updated_state = stream.get_updated_state(
        current_stream_state={"date": "2021-01-25T00:00:00Z"},
        latest_record={"date": "2021-02-25T00:00:00Z"})

    assert updated_state == {"date": "2021-02-25T00:00:00Z"}


def test_cohorts_stream():
    # tested in itaseskii:mixpanel-incremental-syncs
    return None


def test_funnels_list_stream(requests_mock, funnels_list_response):
    requests_mock.register_uri("GET", MIXPANEL_BASE_URL + "funnels/list", funnels_list_response)

    stream = FunnelsList(authenticator=MagicMock())

    records = stream.read_records(sync_mode=SyncMode.full_refresh)

    records_length = sum(1 for _ in records)
    assert records_length == 1


def test_funnels_stream(requests_mock, config, funnels_response, funnels_list_response):
    requests_mock.register_uri("GET", MIXPANEL_BASE_URL + "funnels?funnel_id=1", funnels_response)
    requests_mock.register_uri("GET", MIXPANEL_BASE_URL + "funnels/list", funnels_list_response)

    stream = Funnels(authenticator=MagicMock(), **config)

    stream_slices = stream.stream_slices(sync_mode=SyncMode.incremental)

    records_arr = []
    for stream_slice in stream_slices:
        records = stream.read_records(sync_mode=SyncMode.incremental, stream_slice=stream_slice)
        for record in records:
            records_arr.append(record)

    assert len(records_arr) == 4


def test_engage_schema(requests_mock, engage_schema_response):
    requests_mock.register_uri("GET", MIXPANEL_BASE_URL + "engage/properties", engage_schema_response)

    stream = EngageSchema(authenticator=MagicMock())

    records = stream.read_records(sync_mode=SyncMode.full_refresh)

    records_length = sum(1 for _ in records)
    assert records_length == 3


def test_engage_stream():
    # tested in itaseskii:mixpanel-incremental-syncs
    return None


def test_cohort_members_stream():
    # tested in itaseskii:mixpanel-incremental-syncs
    return None


def test_annotations_stream(requests_mock, annotations_response):
    requests_mock.register_uri("GET", MIXPANEL_BASE_URL + "annotations", annotations_response)

    stream = Annotations(authenticator=MagicMock())

    stream_slice = {"start_date": "2017-01-25T00:00:00Z", "end_date": "2017-02-25T00:00:00Z"}
    # read records for single slice
    records = stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)

    records_length = sum(1 for _ in records)
    assert records_length == 2


def test_revenue_stream(requests_mock, revenue_response):
    requests_mock.register_uri("GET", MIXPANEL_BASE_URL + "engage/revenue", revenue_response)

    stream = Revenue(authenticator=MagicMock())

    stream_slice = {"start_date": "2017-01-25T00:00:00Z", "end_date": "2017-02-25T00:00:00Z"}
    # read records for single slice
    records = stream.read_records(sync_mode=SyncMode.incremental, stream_slice=stream_slice)

    records_length = sum(1 for _ in records)
    assert records_length == 2


def test_export_schema(requests_mock, export_schema_response):
    requests_mock.register_uri("GET", MIXPANEL_BASE_URL + "events/properties/top", export_schema_response)

    stream = ExportSchema(authenticator=MagicMock())

    records = stream.read_records(sync_mode=SyncMode.full_refresh)

    records_length = sum(1 for _ in records)
    assert records_length == 10


def test_export_stream(requests_mock, export_response):
    requests_mock.register_uri("GET", MIXPANEL_DATA_BASE_URL + "export", export_response)

    stream = Export(authenticator=MagicMock())

    stream_slice = {"start_date": "2017-01-25T00:00:00Z", "end_date": "2017-02-25T00:00:00Z"}
    # read records for single slice
    records = stream.read_records(sync_mode=SyncMode.incremental, stream_slice=stream_slice)

    records_length = sum(1 for _ in records)
    assert records_length == 1
