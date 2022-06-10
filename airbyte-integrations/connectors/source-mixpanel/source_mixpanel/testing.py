#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta
from functools import wraps

import pendulum
from airbyte_cdk.logger import AirbyteLogger

from .streams import Funnels

AVAILABLE_TESTING_RANGE_DAYS = 30


def funnel_slices_patched(self: Funnels, sync_mode):
    """
    Return only first result from funnels
    """
    funnel_slices_values = self.get_funnel_slices(sync_mode)
    return [funnel_slices_values[0]] if funnel_slices_values else funnel_slices_values


def adapt_streams_if_testing(func):
    """
    Due to API limitations (60 requests per hour) there is unavailable to make acceptance tests in normal mode,
    so we're reducing amount of requests by, if `is_testing` flag is set in config:

    1. Take time range in only 1 month
    2. Patch Funnels, so we download data only for one Funnel entity
    3. Removing RPS limit for faster testing
    """

    @wraps(func)
    def wrapper(self, config):
        is_testing = config.get("is_testing", False)
        if not is_testing:
            return func(self, config)

        AirbyteLogger().log("INFO", "SOURCE IN TESTING MODE, DO NOT USE IN PRODUCTION!")
        tzone = pendulum.timezone(config.get("project_timezone", "US/Pacific"))
        now = datetime.now(tzone).date()
        # 1. Take time range in only 1 month
        config["start_date"] = now - timedelta(days=AVAILABLE_TESTING_RANGE_DAYS)

        # 2. Patch Funnels, so we download data only for one Funnel entity
        Funnels.funnel_slices = funnel_slices_patched

        streams = func(self, config)

        for stream in streams:
            stream.reqs_per_hour_limit = 0
        return streams

    return wrapper
