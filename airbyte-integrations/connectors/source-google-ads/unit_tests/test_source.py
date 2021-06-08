from source_google_ads.source import chunk_date_range, AdGroupAdReport
from dateutil.relativedelta import *


def test_chunk_date_range():
    start_date = "2021-03-04"
    end_date = "2021-05-04"
    conversion_window = 14
    field = "date"
    response = chunk_date_range(start_date, end_date, conversion_window, field)
    assert [{'date': '2021-02-18'}, {'date': '2021-03-18'},
            {'date': '2021-04-18'}] == response


"""
This won't work until we get sample credentials 
"""

# SAMPLE_CONFIG = {
#   "developer_token": "developer_token",
#   "client_id": "client_id",
#   "client_secret": "client_secret",
#   "refresh_token": "refresh_token",
#   "start_date": "start_date",
#   "customer_id": "customer_id"
# }


# def test_get_updated_state():
#     client = AdGroupAdReport(SAMPLE_CONFIG)
#     current_state_stream = {}
#     latest_record = {"segments.date": "2020-01-01"}

#     new_stream_state = client.get_updated_state(current_state_stream, latest_record)
#     assert new_stream_state == {'segments.date': '2020-01-01'}

#     current_state_stream = {'segments.date': '2020-01-01'}
#     latest_record = {"segments.date": "2020-02-01"}
#     new_stream_state = client.get_updated_state(current_state_stream, latest_record)
#     assert new_stream_state == {'segments.date': '2020-02-01'}
