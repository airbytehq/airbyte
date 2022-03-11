
from source_dv_360.streams import chunk_date_range



SAMPLE_CONFIG = {
    "credentials": {
        "developer_token": "developer_token",
        "client_id": "client_id",
        "client_secret": "client_secret",
        "refresh_token": "refresh_token",
    },
    "customer_id": "customer_id",
}


def test_chunk_date_range():
    start_date = "2022-01-01"
    end_date = "2022-02-20"
    range_days = 15
    field = "date"
    response = chunk_date_range(field, start_date, end_date, range_days)
    assert [
        {"start_date": "2022-01-01", "end_date": "2022-01-15"},
        {"start_date": "2022-01-16", "end_date": "2022-01-31"},
        {"start_date": "2022-02-01", "end_date": "2022-02-15"},
        {"start_date": "2022-02-16", "end_date": "2022-01-20"}
    ] == response