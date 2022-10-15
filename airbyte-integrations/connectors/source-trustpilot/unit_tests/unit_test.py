import datetime
import json

import pytest
import requests
from airbyte_cdk.sources.declarative.datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from jsonschema import validate
from requests_mock import Mocker

from source_trustpilot.source import TrustpilotExtractor, TrustpilotStreamSlicer
from test_data.data import REVIEWS_STREAM_RESPONSE

config_val = {
    "app_name": "free-now.com",
    "start_date": "2022-01-01",
    "timeout_milliseconds": 0
}

options_val = {
    '$options': {
        'name': 'reviews',
        'primary_key': '@id',
        'stream_cursor_field': 'datePublished',
        'path': "/review/{{ config['app_name'] }}"
    },
    'config': config_val,
    'name': 'reviews',
    'primary_key': '@id',
    'stream_cursor_field': 'datePublished',
    'path': "/review/{{ config['app_name'] }}"
}


@pytest.mark.parametrize(
    "config,options",
    [
        (config_val, options_val)
    ],
)
def test_trustpilot_extractor(requests_mock: Mocker, config, options):
    extractor = TrustpilotExtractor(options)

    reviews_url = "https://trustpilot.com/review/free-now.com"
    requests_mock.get(reviews_url + "?languages=all&sort=recency", text=REVIEWS_STREAM_RESPONSE)
    response = requests.get(reviews_url, params={
        "languages": "all",
        "sort": "recency"
    })
    records = extractor.extract_records(response)
    record_schema = json.load(open("./source_trustpilot/schemas/reviews.json"))
    for record in records:
        assert (validate(record, record_schema) is None)


@pytest.mark.parametrize(
    "config,options",
    [
        (config_val, options_val)
    ],
)
def test_trustpilot_stream_slicer(requests_mock: Mocker, config, options):
    start_datetime = MinMaxDatetime(
        datetime=InterpolatedString(string="{{ config['start_date'] }}",
                                    default="{{ config['start_date'] }}", options=options),
        datetime_format='%Y-%m-%d', options=options)
    cursor_field = InterpolatedString(string="{{ options['stream_cursor_field'] }}",
                                      default="{{ options['stream_cursor_field'] }}",
                                      options=options)
    datetime_format = '%Y-%m-%dT%H:%M:%S.%fZ'

    stream_slicer = TrustpilotStreamSlicer(
        config=config,
        options=options,
        cursor_field=cursor_field,
        start_datetime=start_datetime,
        datetime_format=datetime_format
    )

    # only config
    state = stream_slicer.get_stream_state()
    assert (stream_slicer.parse_date(state["new_datePublished"]) ==
            datetime.datetime.strptime(config["start_date"], "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc))

    # saved state
    sample_state = {
        "new_datePublished": "2022-09-01T00:00:00.000Z"
    }
    stream_slicer.update_cursor(sample_state)
    state = stream_slicer.get_stream_state()
    assert (stream_slicer.parse_date(state["new_datePublished"]) ==
            stream_slicer.parse_date(sample_state["new_datePublished"]))

    # new state and last record
    last_record = {
        "datePublished": "2022-10-15T23:13:01.000Z"
    }
    stream_slicer.update_cursor(state, last_record)
    state = stream_slicer.get_stream_state()
    assert (stream_slicer.parse_date(state["new_datePublished"]) ==
            stream_slicer.parse_date(last_record["datePublished"]))
