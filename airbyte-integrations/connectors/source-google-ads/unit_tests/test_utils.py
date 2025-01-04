#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from datetime import datetime
from unittest.mock import Mock

import backoff
import pytest
from source_google_ads import SourceGoogleAds
from source_google_ads.utils import GAQL, generator_backoff

from airbyte_cdk.utils import AirbyteTracedException


def test_parse_GAQL_ok():
    sql = GAQL.parse("SELECT field FROM table")
    assert sql.fields == ("field",)
    assert sql.resource_name == "table"
    assert sql.where == ""
    assert sql.order_by == ""
    assert sql.limit is None
    assert sql.parameters == ""
    assert str(sql) == "SELECT field FROM table"

    sql = GAQL.parse("SELECT field1, field2 FROM x_Table ")
    assert sql.fields == ("field1", "field2")
    assert sql.resource_name == "x_Table"
    assert sql.where == ""
    assert sql.order_by == ""
    assert sql.limit is None
    assert sql.parameters == ""
    assert str(sql) == "SELECT field1, field2 FROM x_Table"

    sql = GAQL.parse("SELECT field1, field2 FROM x_Table WHERE date = '2020-01-01' ")
    assert sql.fields == ("field1", "field2")
    assert sql.resource_name == "x_Table"
    assert sql.where == "date = '2020-01-01'"
    assert sql.order_by == ""
    assert sql.limit is None
    assert sql.parameters == ""
    assert str(sql) == "SELECT field1, field2 FROM x_Table WHERE date = '2020-01-01'"

    sql = GAQL.parse("SELECT field1, field2 FROM x_Table WHERE date = '2020-01-01' ORDER  BY field2, field1 ")
    assert sql.fields == ("field1", "field2")
    assert sql.resource_name == "x_Table"
    assert sql.where == "date = '2020-01-01'"
    assert sql.order_by == "field2, field1"
    assert sql.limit is None
    assert sql.parameters == ""
    assert str(sql) == "SELECT field1, field2 FROM x_Table WHERE date = '2020-01-01' ORDER BY field2, field1"

    sql = GAQL.parse("SELECT t.field1, t.field2 FROM x_Table ORDER  BY field2, field1 LIMIT 10 ")
    assert sql.fields == ("t.field1", "t.field2")
    assert sql.resource_name == "x_Table"
    assert sql.where == ""
    assert sql.order_by == "field2, field1"
    assert sql.limit == 10
    assert sql.parameters == ""
    assert str(sql) == "SELECT t.field1, t.field2 FROM x_Table ORDER BY field2, field1 LIMIT 10"

    sql = GAQL.parse(
        """
        SELECT field1, field2
          FROM x_Table
         WHERE date = '2020-01-01'
      ORDER BY field2 ASC, field1 DESC
         LIMIT 10
    PARAMETERS include_drafts=true """
    )

    assert sql.fields == ("field1", "field2")
    assert sql.resource_name == "x_Table"
    assert sql.where == "date = '2020-01-01'"
    assert sql.order_by == "field2 ASC, field1 DESC"
    assert sql.limit == 10
    assert sql.parameters == "include_drafts=true"
    assert (
        str(sql)
        == "SELECT field1, field2 FROM x_Table WHERE date = '2020-01-01' ORDER BY field2 ASC, field1 DESC LIMIT 10 PARAMETERS include_drafts=true"
    )


@pytest.mark.parametrize(
    "config",
    [
        {"custom_queries_array": [{"query": "SELECT field1, field2 FROM x_Table2", "table_name": "test_table"}]},
        {"custom_queries_array": [{"query": "SELECT field1, field2 FROM x_Table WHERE ", "table_name": "test_table"}]},
        {"custom_queries_array": [{"query": "SELECT field1, , field2 FROM table", "table_name": "test_table"}]},
        {"custom_queries_array": [{"query": "SELECT fie ld1, field2 FROM table", "table_name": "test_table"}]},
    ],
)
def test_parse_GAQL_fail(config):
    with pytest.raises(AirbyteTracedException) as e:
        SourceGoogleAds._validate_and_transform(config)
    expected_message = "The custom GAQL query test_table failed. Validate your GAQL query with the Google Ads query validator. https://developers.google.com/google-ads/api/fields/v17/query_validator"
    assert e.value.message == expected_message


@pytest.mark.parametrize(
    "query, fields",
    [
        (
            """
SELECT
  campaign.id,
  campaign.name,
  campaign.status,
  metrics.impressions
FROM campaign
WHERE campaign.status = 'PAUSED'
AND metrics.impressions > 100
ORDER BY campaign.status
    """,
            ["campaign.id", "campaign.name", "campaign.status", "metrics.impressions"],
        ),
        (
            """
SELECT
  campaign.accessible_bidding_strategy,
  segments.ad_destination_type,
  campaign.start_date,
  campaign.end_date
FROM campaign
    """,
            ["campaign.accessible_bidding_strategy", "segments.ad_destination_type", "campaign.start_date", "campaign.end_date"],
        ),
    ],
)
def test_get_query_fields(query, fields):
    assert list(GAQL.parse(query).fields) == fields


def test_generator_backoff_retries_until_success():
    tries = 0

    def flaky_function():
        nonlocal tries  # Declare tries as nonlocal to modify it within the function
        if tries < 2:
            tries += 1
            raise ValueError("Simulated failure")
        else:
            yield "Success"

    # Mock on_backoff callable
    mock_on_backoff = Mock()

    # Apply the decorator to the flaky_function
    decorated_flaky_function = generator_backoff(
        wait_gen=backoff.expo,
        exception=ValueError,
        max_tries=4,
        max_time=5,
        on_backoff=mock_on_backoff,
        factor=2,
    )(flaky_function)

    # Start the clock
    start_time = datetime.now()

    # Run the decorated function and collect results
    results = list(decorated_flaky_function())

    # Check that the function succeeded after retries
    assert results == ["Success"]

    # Check that the function was retried the correct number of times
    assert mock_on_backoff.call_count == 2

    # Check that the elapsed time is reasonable
    elapsed_time = (datetime.now() - start_time).total_seconds()
    # The wait times are 3 and then 2 seconds, so the elapsed time should be at least 5 seconds
    assert elapsed_time >= 5

    # Check that on_backoff was called with the correct parameters
    expected_calls = [
        {
            "target": flaky_function,
            "args": (),
            "kwargs": {},
            "tries": 1,
            "elapsed": pytest.approx(0.1, abs=0.1),
            "wait": pytest.approx(2, abs=0.1),
            "exception": "Simulated failure",
        },
        {
            "target": flaky_function,
            "args": (),
            "kwargs": {},
            "tries": 2,
            "elapsed": pytest.approx(2, abs=0.1),
            "wait": pytest.approx(3, abs=0.1),
            "exception": "Simulated failure",
        },
    ]

    # Convert actual calls to a list of dictionaries
    actual_calls = [{**c.args[0], "exception": str(c.args[0]["exception"])} for c in mock_on_backoff.call_args_list]
    print(actual_calls)

    # Compare each expected call with the actual call
    for expected, actual in zip(expected_calls, actual_calls):
        assert expected == actual
