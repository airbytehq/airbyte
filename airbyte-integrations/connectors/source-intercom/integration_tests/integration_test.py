#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
import time
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Mapping
from unittest.mock import patch

import pytest
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from requests.exceptions import HTTPError
from source_intercom.source import Companies, ConversationParts, SourceIntercom, VersionApiAuthenticator

LOGGER = AirbyteLogger()
# from unittest.mock import Mock

HERE = Path(__file__).resolve().parent


@pytest.fixture(scope="module")
def stream_attributes() -> Mapping[str, str]:
    filename = HERE.parent / "secrets/config.json"
    with open(filename) as json_file:
        return json.load(json_file)


@pytest.mark.skip(reason="need to refresh this test, it is very slow")
@pytest.mark.parametrize(
    "version,not_supported_streams,custom_companies_data_field",
    (
        (1.0, ["company_segments", "company_attributes", "contact_attributes"], "companies"),
        (1.1, ["company_segments", "company_attributes", "contact_attributes"], "companies"),
        (1.2, ["company_segments", "company_attributes", "contact_attributes"], "companies"),
        (1.3, ["company_segments", "company_attributes", "contact_attributes"], "companies"),
        (1.4, ["company_segments"], "companies"),
        (2.0, [], "data"),
        (2.1, [], "data"),
        (2.2, [], "data"),
        (2.3, [], "data"),
    ),
)
def test_supported_versions(stream_attributes, version, not_supported_streams, custom_companies_data_field):
    class CustomVersionApiAuthenticator(VersionApiAuthenticator):
        relevant_supported_version = str(version)

    authenticator = CustomVersionApiAuthenticator(token=stream_attributes["access_token"])
    for stream in SourceIntercom().streams(deepcopy(stream_attributes)):
        stream._authenticator = authenticator
        if stream.name == "companies":
            stream.data_fields = [custom_companies_data_field]
        elif hasattr(stream, "parent_stream_class") and stream.parent_stream_class == Companies:
            stream.parent_stream_class.data_fields = [custom_companies_data_field]

        if stream.name in not_supported_streams:
            LOGGER.info(f"version {version} shouldn't be supported the stream '{stream.name}'")
            with pytest.raises(HTTPError) as err:
                for slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
                    next(stream.read_records(sync_mode=None, stream_slice=slice), None)
                    break
            # example of response errors:
            # {"type": "error.list", "request_id": "000hjqhpf95ef3b8f8v0",
            #  "errors": [{"code": "intercom_version_invalid", "message": "The requested version could not be found"}]}
            assert len(err.value.response.json()["errors"]) > 0
            err_data = err.value.response.json()["errors"][0]
            LOGGER.info(f"version {version} doesn't support the stream '{stream.name}', error: {err_data}")
        else:
            LOGGER.info(f"version {version} should be supported the stream '{stream.name}'")
            for slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
                records = stream.read_records(sync_mode=None, stream_slice=slice)
                if stream.name == "companies":
                    # need to read all records for scroll resetting
                    list(records)
                else:
                    next(records, None)


def test_companies_scroll(stream_attributes):
    authenticator = VersionApiAuthenticator(token=stream_attributes["access_token"])
    stream1 = Companies(authenticator=authenticator)
    stream2 = Companies(authenticator=authenticator)
    stream3 = Companies(authenticator=authenticator)

    # read the first stream and stop
    for slice in stream1.stream_slices(sync_mode=SyncMode.full_refresh):
        next(stream1.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice), None)
        break

    start_time = time.time()
    # read all records
    records = []
    for slice in stream2.stream_slices(sync_mode=SyncMode.full_refresh):
        records += list(stream2.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice))
    assert len(records) == 3
    assert (time.time() - start_time) > 60.0

    start_time = time.time()
    # read all records
    records = []
    for slice in stream3.stream_slices(sync_mode=SyncMode.full_refresh):
        records += list(stream3.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice))
    assert len(records) == 3
    assert (time.time() - start_time) < 5.0


@patch("source_intercom.source.Companies.can_use_scroll", lambda *args: False)
def test_switch_to_standard_endpoint(stream_attributes):
    authenticator = VersionApiAuthenticator(token=stream_attributes["access_token"])
    start_date = datetime.strptime(stream_attributes["start_date"], "%Y-%m-%dT%H:%M:%SZ").timestamp()
    stream1 = Companies(authenticator=authenticator)
    stream2 = Companies(authenticator=authenticator)
    stream3 = ConversationParts(authenticator=authenticator, start_date=start_date)

    # read the first stream and stop
    for slice in stream1.stream_slices(sync_mode=SyncMode.full_refresh):
        next(stream1.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice), None)
        break

    start_time = time.time()
    # read all records
    records = []
    assert stream2._endpoint_type == Companies.EndpointType.scroll
    for slice in stream2.stream_slices(sync_mode=SyncMode.full_refresh):
        records += list(stream2.read_records(sync_mode=SyncMode, stream_slice=slice))
    assert stream2._endpoint_type == Companies.EndpointType.standard
    assert stream2._total_count == 3
    assert len(records) == 3
    assert (time.time() - start_time) < 5.0

    start_time = time.time()
    # read all children records
    records = []
    for slice in stream3.stream_slices(sync_mode=SyncMode.full_refresh):
        records += list(stream3.read_records(sync_mode=SyncMode, stream_slice=slice))
    assert len(records) == 12
    assert (time.time() - start_time) < 5.0
