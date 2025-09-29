#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.state_builder import StateBuilder

from .conftest import read_from_stream


@pytest.mark.parametrize(
    ("start_date", "stream_state", "expected_records"),
    (
        (
            None,
            {},
            [
                {"id": "campaign_id_1", "ad_account_id": "ad_account_id", "updated_time": 1711929600},
                {"id": "campaign_id_2", "ad_account_id": "ad_account_id", "updated_time": 1712102400},
            ],
        ),
        ("2024-04-02", {}, [{"id": "campaign_id_2", "ad_account_id": "ad_account_id", "updated_time": 1712102400}]),
        (
            "2024-03-30",
            {
                "states": [
                    {"partition": {"id": "ad_account_id", "parent_slice": {}}, "cursor": {"updated_time": 1712016000}},
                ],
            },
            [{"id": "campaign_id_2", "ad_account_id": "ad_account_id", "updated_time": 1712102400}],
        ),
        (
            "2024-04-02",
            {
                "states": [
                    {"partition": {"id": "ad_account_id", "parent_slice": {}}, "cursor": {"updated_time": 1711929599}},
                ],
            },
            [{"id": "campaign_id_2", "ad_account_id": "ad_account_id", "updated_time": 1712102400}],
        ),
        (
            None,
            {
                "states": [
                    {"partition": {"id": "ad_account_id", "parent_slice": {}}, "cursor": {"updated_time": 1712016000}},
                ],
            },
            [{"id": "campaign_id_2", "ad_account_id": "ad_account_id", "updated_time": 1712102400}],
        ),
    ),
)
def test_semi_incremental_read(requests_mock, test_config, start_date, stream_state, expected_records):
    if start_date is None:
        del test_config["start_date"]
    else:
        test_config["start_date"] = start_date

    ad_account_id = "ad_account_id"
    requests_mock.get(url="https://api.pinterest.com/v5/ad_accounts", json={"items": [{"id": ad_account_id}]})
    requests_mock.get(
        url=f"https://api.pinterest.com/v5/ad_accounts/{ad_account_id}/campaigns",
        json={
            "items": [
                {"id": "campaign_id_1", "ad_account_id": ad_account_id, "updated_time": 1711929600},  # 2024-04-01
                {"id": "campaign_id_2", "ad_account_id": ad_account_id, "updated_time": 1712102400},  # 2024-04-03
            ],
        },
    )

    state = (
        StateBuilder()
        .with_stream_state(
            "campaigns",
            stream_state,
        )
        .build()
    )

    actual_records = [
        record.record.data for record in read_from_stream(test_config, "campaigns", sync_mode=SyncMode.incremental, state=state).records
    ]
    assert actual_records == expected_records
