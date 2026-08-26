# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import datetime, timedelta, timezone

import yaml

from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime


# PayPal's customer-disputes API rejects update_time_after older than 180 days with
# INVALID_DATE_RANGE. The resolved start boundary is evaluated once at stream build time and
# reused for every request that follows, so it needs margin inside the window - landing exactly
# on 180 days means every request is already out of range by the time it is sent.
def test_list_disputes_start_datetime_stays_inside_paypal_180_day_window(manifest_path):
    manifest = yaml.safe_load(manifest_path.read_text())
    start_datetime = manifest["definitions"]["streams"]["list_disputes"]["incremental_sync"]["start_datetime"]

    resolved = MinMaxDatetime(
        datetime=start_datetime["datetime"],
        # the manifest's "%Y-%m-%dT%H:%M:%S.%_msZ" needs the CDK DatetimeParser; the pinned
        # test CDK parses with strptime, which rejects %_ms - %f reads the same values
        datetime_format="%Y-%m-%dT%H:%M:%S.%fZ",
        min_datetime=start_datetime.get("min_datetime", ""),
        parameters={},
    ).get_datetime(config={})

    age = datetime.now(timezone.utc) - resolved
    assert age < timedelta(days=180), f"start boundary is {age} old, PayPal rejects anything past 180 days"
