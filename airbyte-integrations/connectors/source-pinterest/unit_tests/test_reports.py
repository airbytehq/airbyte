#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import responses
from source_pinterest.utils import get_analytics_columns


@responses.activate
def test_request_body_json(analytics_report_stream, date_range):
    granularity = 'DAY'
    columns = get_analytics_columns()

    expected_body = {
        'start_date': date_range['start_date'],
        'end_date': date_range['end_date'],
        'granularity': granularity,
        'columns': columns.split(','),
        'level': analytics_report_stream.level,
    }

    body = analytics_report_stream.request_body_json(date_range)
    assert body == expected_body


@responses.activate
def test_read_records(analytics_report_stream, date_range):
    report_download_url = 'https://download.report'
    report_request_url = 'https://api.pinterest.com/v5/ad_accounts/123/reports'

    final_report_status = {
         'report_status': 'FINISHED',
         'url': report_download_url
    }

    initial_response = {
         'report_status': "IN_PROGRESS",
         'token': 'token',
         'message': ''
    }

    final_response = {"campaign_id": [{"metric": 1}]}

    responses.add(responses.POST, report_request_url, json=initial_response)
    responses.add(responses.GET, report_request_url, json=final_report_status, status=200)
    responses.add(responses.GET, report_download_url, json=final_response, status=200)

    sync_mode = 'full_refresh'
    cursor_field = ['last_updated']
    stream_state = {
        'start_date': '2023-01-01',
        'end_date': '2023-01-31',
    }

    records = analytics_report_stream.read_records(sync_mode, cursor_field, date_range, stream_state)
    expected_record = {"metric": 1}

    assert next(records) == expected_record
    assert len(responses.calls) == 3
    assert responses.calls[0].request.url == report_request_url
