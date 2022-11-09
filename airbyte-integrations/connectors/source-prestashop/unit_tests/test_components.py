#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
from unittest.mock import MagicMock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.offset_increment import OffsetIncrement
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption
from freezegun import freeze_time
from source_prestashop.components import LimitOffsetPaginator, NoSlicer


def test_limit_offset_paginator():
    limit_offset_option = RequestOption(inject_into="request_parameter", field_name="limit", options=None)
    pagination_strategy = OffsetIncrement(page_size=2, options=None)
    paginator = LimitOffsetPaginator(limit_offset_option=limit_offset_option, pagination_strategy=pagination_strategy, options=None)
    paginator.reset()
    assert paginator.get_request_params() == {"limit": "2"}
    next_page_token = paginator.next_page_token(response=MagicMock(), last_records=[{}, {}])
    assert next_page_token == {"next_page_token": 2}
    assert paginator.get_request_params() == {"limit": "2,2"}
    next_page_token = paginator.next_page_token(response=MagicMock(), last_records=[{}])
    assert next_page_token is None


@freeze_time("2022-01-01 00:00:01")
def test_no_slicer():
    cursor_field = InterpolatedString(string="date_upd", options=None)
    primary_key = InterpolatedString(string="id", options=None)

    # test full_refresh
    slicer = NoSlicer(config={}, cursor_field=cursor_field, primary_key=primary_key, options=None)
    slicer._cursor_end = datetime.datetime.utcnow()
    assert list(slicer.stream_slices(sync_mode=SyncMode.full_refresh, stream_state={})) == [{}]
    assert slicer.get_request_params() == {"date": "1", "sort": "[date_upd_ASC,id_ASC]"}
    slicer.update_cursor(stream_slice={}, last_record={"date_upd": "2021-07-23 23:18:07"})
    assert slicer.get_request_params() == {"date": "1", "sort": "[date_upd_ASC,id_ASC]"}
    assert slicer.get_stream_state() == {"date_upd": "2021-07-23 23:18:07"}

    # test incremental
    slicer = NoSlicer(config={}, cursor_field=cursor_field, primary_key=primary_key, options=None)
    slicer._cursor_end = datetime.datetime.utcnow()
    slicer.update_cursor(stream_slice={"date_upd": "2021-07-23 23:18:07"})
    assert list(slicer.stream_slices(sync_mode=SyncMode.incremental, stream_state={})) == [{"date_upd": "2021-07-23 23:18:07"}]
    assert slicer.get_request_params() == {
        "date": "1",
        "sort": "[date_upd_ASC,id_ASC]",
        "filter[date_upd]": "[2021-07-23 23:18:07,2022-01-01 00:00:01]",
    }
    slicer.update_cursor(stream_slice={"date_upd": "2021-07-23 23:18:07"}, last_record={"date_upd": "2021-07-23 23:18:08"})
    assert slicer.get_request_params() == {
        "date": "1",
        "sort": "[date_upd_ASC,id_ASC]",
        "filter[date_upd]": "[2021-07-23 23:18:08,2022-01-01 00:00:01]",
    }
    assert slicer.get_stream_state() == {"date_upd": "2021-07-23 23:18:08"}
