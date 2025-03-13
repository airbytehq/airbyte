#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import timedelta

from airbyte_cdk.sources.streams.call_rate import APIBudget, HttpRequestMatcher, MovingWindowCallRatePolicy, Rate


DEFAULT_API_BUDGET = APIBudget(
    policies=[MovingWindowCallRatePolicy(rates=[Rate(limit=60, interval=timedelta(hours=1.0))], matchers=[HttpRequestMatcher()])]
)
