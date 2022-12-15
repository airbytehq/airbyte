#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from functools import wraps

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
    so we're reducing amount of requests by, if `_testing` flag is set in config:

    1. Patch Funnels, so we download data only for one Funnel entity
    2. Removing RPS limit for faster testing
    """

    @wraps(func)
    def wrapper(self, config):
        if not config.get("_testing"):
            return func(self, config)

        # Patch Funnels, so we download data only for one Funnel entity
        Funnels.funnel_slices = funnel_slices_patched

        streams = func(self, config)

        for stream in streams:
            stream.reqs_per_hour_limit = 0
        return streams

    return wrapper


def adapt_validate_if_testing(func):
    """
    Due to API limitations (60 requests per hour) there is unavailable to make acceptance tests in normal mode,
    so we're reducing amount of requests by, if `_testing` flag is set in config:

    1. Take time range in only 1 month
    """

    @wraps(func)
    def wrapper(self, config):
        config = func(self, config)
        if config.get("_testing"):
            logger = logging.getLogger("airbyte")
            logger.info("SOURCE IN TESTING MODE, DO NOT USE IN PRODUCTION!")
            # Take time range in only 1 month
            if (config["end_date"] - config["start_date"]).days > AVAILABLE_TESTING_RANGE_DAYS:
                config["start_date"] = config["end_date"].subtract(days=AVAILABLE_TESTING_RANGE_DAYS)
        return config

    return wrapper
