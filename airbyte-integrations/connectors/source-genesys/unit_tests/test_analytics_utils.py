import hashlib
from datetime import datetime

from source_genesys.analytics_utils import (
    generate_query, 
    create_surrogate_key, 
    str_timestamp_to_datetime, 
    split_utc_timestamp_interval,
    parse_analytics_records
)


def test_generate_query():
    window_date_str = "2023-05-17"
    metrics = ["metric1", "metric2"]
    expected_query = {
        "interval": "2023-05-17T00:00:00.000Z/2023-05-17T23:59:59.000Z",
        "metrics": metrics
    }

    result = generate_query(window_date_str, metrics)

    assert result == expected_query


def test_create_surrogate_key():
    key1 = "abc"
    key2 = 123
    key3 = "xyz"

    expected_key = hashlib.md5(f"{key1}{key2}{key3}".encode("utf-8")).hexdigest()
    result = create_surrogate_key(key1, key2, key3)

    assert result == expected_key


def test_str_timestamp_to_datetime():
    str_timestamp = "2023-05-17"
    expected_datetime = datetime(2023, 5, 17)

    str_result = str_timestamp_to_datetime(str_timestamp)
    assert str_result == expected_datetime

    datetime_timestamp = datetime(2023, 5, 17)
    datetime_result = str_timestamp_to_datetime(datetime_timestamp)

    assert datetime_result == expected_datetime

    invalid_timestamp = 123
    expected_result = invalid_timestamp
    invalid_result = str_timestamp_to_datetime(invalid_timestamp)

    assert invalid_result, expected_result


def test_split_utc_timestamp_interval():
    timestamp_range = "2023-05-17T00:00:00.000Z/2023-05-17T23:59:59.000Z"
    expected_start = datetime(2023, 5, 17, 0, 0, 0)
    expected_end = datetime(2023, 5, 17, 23, 59, 59)

    result_start, result_end = split_utc_timestamp_interval(timestamp_range)

    assert result_start == expected_start
    assert result_end == expected_end


def test_parse_analytics_records():
    client_id = "123"
    results_json = {
        "results":
            [
                {
                    "group": {
                        "mediaType": "email"
                    },
                    "data": [
                        {
                            "interval": "2023-05-17T00:00:00.000Z/2023-05-17T23:59:59.000Z",
                            "metrics": [
                                {
                                    "metric": "opens",
                                    "stats": {
                                        "max": 100,
                                        "min": 50,
                                        "count": 200,
                                        "sum": 5000
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
    }

    expected_unique_id = "146f8971294126933ccfffbbb5301e6c"
    expected_start_timestamp = datetime(2023, 5, 17, 0, 0, 0)
    expected_end_timestamp = datetime(2023, 5, 17, 23, 59, 59)

    expected_metric_record = {
        "unique_id": expected_unique_id,
        "client_id": client_id,
        "media_type": "email",
        "interval_start": expected_start_timestamp,
        "interval_end": expected_end_timestamp,
        "metric_name": "opens",
        "max": 100,
        "min": 50,
        "count": 200,
        "sum": 5000
    }

    records = list(parse_analytics_records(client_id, results_json["results"]))
    assert len(records) == 1
    assert records[0] == expected_metric_record
