# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker

from .config import ConfigBuilder
from .request_builder import request_for
from .response_builder import response_for


STREAMS = [
    ("organizations", "OrgID"),
    ("media", "EntityMediaID"),
    ("links", "EntityLinkID"),
    ("facilityaddresses", "FacilityAddressID"),
    ("facilities", "FacilityID"),
    ("events", "EventID"),
    ("activities", "ActivityID"),
    ("campsites", "CampsiteID"),
    ("permits", "PermitEntranceID"),
    ("recreationareaaddresses", "RecAreaAddressID"),
    ("recreationareas", "RecAreaID"),
    ("tours", "TourID"),
]


@pytest.mark.parametrize("stream,primary_key", STREAMS)
@pytest.mark.parametrize("pages", [[[]], [[7, 9]], [list(range(1, 51)), [51, 52]]], ids=["empty", "short", "paginated"])
def test_full_refresh(http_mocker: HttpMocker, stream: str, primary_key: str, pages: list[list[int]]) -> None:
    config = ConfigBuilder().with_query(stream, "forest").build()
    requests = []
    for index, ids in enumerate(pages):
        request = request_for(stream, config, None if index == 0 else index * 50)
        requests.append(request)
        http_mocker.get(request, response_for(stream, primary_key, ids))

    catalog = CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build()
    output = read(get_source(config), config, catalog)
    assert not output.errors
    assert [record.record.data[primary_key] for record in output.records] == [
        str(identifier) if stream != "activities" else identifier for page in pages for identifier in page
    ]
    for request in requests:
        http_mocker.assert_number_of_calls(request, 1)
