#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import timedelta

from airbyte_cdk.sources.streams.call_rate import APIBudget, HttpRequestMatcher, MovingWindowCallRatePolicy, Rate


DEFAULT_API_BUDGET = APIBudget(
    policies=[MovingWindowCallRatePolicy(rates=[Rate(limit=1, interval=timedelta(seconds=60.0))], matchers=[HttpRequestMatcher()])]
)
