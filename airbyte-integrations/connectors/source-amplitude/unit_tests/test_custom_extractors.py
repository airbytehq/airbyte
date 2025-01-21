#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

import pytest
import requests
from source_amplitude.components import ActiveUsersRecordExtractor, AverageSessionLengthRecordExtractor


@pytest.mark.parametrize(
    "custom_extractor, data, expected",
    [
        (
            ActiveUsersRecordExtractor,
            {
                "xValues": ["2021-01-01", "2021-01-02"],
                "series": [[1, 5]],
                "seriesCollapsed": [[0]],
                "seriesLabels": [0],
                "seriesMeta": [{"segmentIndex": 0}],
            },
            [{"date": "2021-01-01", "statistics": {0: 1}}, {"date": "2021-01-02", "statistics": {0: 5}}],
        ),
        (
            ActiveUsersRecordExtractor,
            {
                "xValues": ["2021-01-01", "2021-01-02"],
                "series": [],
                "seriesCollapsed": [[0]],
                "seriesLabels": [0],
                "seriesMeta": [{"segmentIndex": 0}],
            },
            [],
        ),
        (
            AverageSessionLengthRecordExtractor,
            {
                "xValues": ["2019-05-23", "2019-05-24"],
                "series": [[2, 6]],
                "seriesCollapsed": [[0]],
                "seriesLabels": [0],
                "seriesMeta": [{"segmentIndex": 0}],
            },
            [{"date": "2019-05-23", "length": 2}, {"date": "2019-05-24", "length": 6}],
        ),
        (
            AverageSessionLengthRecordExtractor,
            {
                "xValues": ["2019-05-23", "2019-05-24"],
                "series": [],
                "seriesCollapsed": [[0]],
                "seriesLabels": [0],
                "seriesMeta": [{"segmentIndex": 0}],
            },
            [],
        ),
    ],
    ids=["ActiveUsers", "EmptyActiveUsers", "AverageSessionLength", "EmptyAverageSessionLength"],
)
def test_parse_response(custom_extractor, data, expected):
    extractor = custom_extractor()
    response = requests.Response()
    response.json = MagicMock(return_value={"data": data})
    result = extractor.extract_records(response)
    assert result == expected
