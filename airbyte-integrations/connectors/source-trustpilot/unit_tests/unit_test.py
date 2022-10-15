import json

import requests
from jsonschema import validate
from requests_mock import Mocker

from source_trustpilot.source import TrustpilotExtractor
from test_data.data import REVIEWS_STREAM_RESPONSE


def test_trustpilot_extractor(requests_mock: Mocker):
    options = {
        'config': {
            "app_name": "free-now.com",
            "start_date": "2022-01-01",
            "timeout_milliseconds": 0
        }
    }
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
