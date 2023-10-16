#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import os
from functools import wraps

from .streams import Funnels


def funnel_slices_patched(self: Funnels, sync_mode):
    """
    Return only first result from funnels
    """
    funnel_slices_values = self.get_funnel_slices(sync_mode)
    single_slice = next(funnel_slices_values, None)
    return [single_slice] if single_slice else []


def adapt_streams_if_testing(func):
    # Patch Funnels, so we download data only for one Funnel entity
    @wraps(func)
    def wrapper(self, config):
        if bool(os.environ.get("PATCH_FUNNEL_SLICES", "")):
            Funnels.funnel_slices = funnel_slices_patched
        return func(self, config)

    return wrapper


def adapt_validate_if_testing(func):
    """
    Due to API limitations (60 requests per hour) it is impossible to run acceptance tests in normal mode,
    so we're reducing amount of requests by aligning start date if `AVAILABLE_TESTING_RANGE_DAYS` flag is set in env variables.
    """

    @wraps(func)
    def wrapper(self, config):
        config = func(self, config)
        available_testing_range_days = int(os.environ.get("AVAILABLE_TESTING_RANGE_DAYS", 0))
        if available_testing_range_days:
            logger = logging.getLogger("airbyte")
            logger.info("SOURCE IN TESTING MODE, DO NOT USE IN PRODUCTION!")
            if (config["end_date"] - config["start_date"]).days > available_testing_range_days:
                config["start_date"] = config["end_date"].subtract(days=available_testing_range_days)
        return config

    return wrapper
