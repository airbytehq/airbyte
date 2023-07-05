#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import os
from functools import wraps

from .streams import Funnels

AVAILABLE_TESTING_RANGE_DAYS = 10


def funnel_slices_patched(self: Funnels, sync_mode):
    """
    Return only first result from funnels
    """
    funnel_slices_values = self.get_funnel_slices(sync_mode)
    single_slice = next(funnel_slices_values, None)
    return [single_slice] if single_slice else []


def adapt_streams_if_testing(func):
    # Patch Funnels, so we download data only for one Funnel entity
    Funnels.funnel_slices = funnel_slices_patched
    return func


def adapt_validate_if_testing(func):
    """
    Due to API limitations (60 requests per hour) there is unavailable to make acceptance tests in normal mode,
    so we're reducing amount of requests by, if `ALIGN_DATE_RANGE` flag is set in env variables:

    1. Take time range in only 1 month
    """

    @wraps(func)
    def wrapper(self, config):
        config = func(self, config)
        if os.environ.get("ALIGN_DATE_RANGE_TO_LAST_N_DAYS", False):
            logger = logging.getLogger("airbyte")
            logger.info("SOURCE IN TESTING MODE, DO NOT USE IN PRODUCTION!")
            # Take time range in only 1 month
            if (config["end_date"] - config["start_date"]).days > AVAILABLE_TESTING_RANGE_DAYS:
                config["start_date"] = config["end_date"].subtract(days=AVAILABLE_TESTING_RANGE_DAYS)
        return config

    return wrapper
