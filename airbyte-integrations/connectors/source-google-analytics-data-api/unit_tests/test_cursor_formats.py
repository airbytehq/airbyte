#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import pytest
import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from unit_tests.conftest import get_source


_CONFIG = {
    "credentials": {
        "auth_type": "Client",
        "client_id": "client-id",
        "client_secret": "client-secret",
        "refresh_token": "refresh-token",
    },
    "date_ranges_start_date": "2026-01-01",
    "date_ranges_end_date": "2026-01-31",
    "window_in_days": 31,
    "property_ids": ["111"],
}


# The state never goes below the start date, and a value the cursor cannot parse leaves it there,
# so every value lies after 2026-01-01.
@pytest.mark.parametrize(
    "dimension, value, expected_state",
    [
        pytest.param("date", "20260115", "2026-01-15", id="date"),
        # `%Y%m` used to match early weeks: week 5 became May 1, months ahead of the data.
        pytest.param("yearWeek", "202705", "2027-01-01", id="yearWeek_early_in_year"),
        # `%Y%m%d` used to match `202745` as April 5.
        pytest.param("yearWeek", "202745", "2027-01-01", id="yearWeek_late_in_year"),
        # `%Y%m%d` used to match `202611` as January 1.
        pytest.param("yearMonth", "202611", "2026-11-01", id="yearMonth"),
        pytest.param("year", "2027", "2027-01-01", id="year"),
    ],
)
def test_cursor_value_is_parsed_with_the_format_of_its_dimension(dimension, value, expected_state):
    config = dict(_CONFIG, custom_reports_array=[{"name": "report", "dimensions": [dimension], "metrics": ["sessions"]}])
    catalog = CatalogBuilder().with_stream("report", SyncMode.incremental).build()

    with requests_mock.Mocker() as http_mocker:
        http_mocker.post(
            "https://www.googleapis.com/oauth2/v4/token",
            json={"access_token": "access-token", "expires_in": 3600},
        )
        http_mocker.get(
            "https://analyticsdata.googleapis.com/v1beta/properties/111/metadata",
            json={"metrics": [{"apiName": "sessions", "type": "TYPE_INTEGER"}]},
        )
        http_mocker.post(
            "https://analyticsdata.googleapis.com/v1beta/properties/111:runReport",
            json={
                "dimensionHeaders": [{"name": dimension}],
                "metricHeaders": [{"name": "sessions", "type": "TYPE_INTEGER"}],
                "rows": [{"dimensionValues": [{"value": value}], "metricValues": [{"value": "7"}]}],
            },
        )
        output = read(get_source(config), config, catalog)

    assert [record.record.data[dimension] for record in output.records] == [value]
    assert output.most_recent_state.stream_state.__dict__[dimension] == expected_state
