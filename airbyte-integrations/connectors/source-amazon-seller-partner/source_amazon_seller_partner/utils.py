#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
import time

from airbyte_cdk.models import FailureType
from airbyte_cdk.utils import AirbyteTracedException


LOG_LEVEL = logging.getLevelName("INFO")
LOGGER = logging.getLogger("airbyte")


class AmazonConfigException(AirbyteTracedException):
    def __init__(self, **kwargs):
        failure_type: FailureType = FailureType.config_error
        super(AmazonConfigException, self).__init__(failure_type=failure_type, **kwargs)


class ReportRateLimits:
    def __init__(self, threshold: int, period_in_minutes: int):
        self.threshold = threshold
        self.period_in_minutes = period_in_minutes

    @property
    def wait_time_in_seconds(self):
        return (self.period_in_minutes / self.threshold) * 60


# https://github.com/airbytehq/alpha-beta-issues/issues/3717#issuecomment-2203717834
STREAM_THRESHOLD_PERIOD = {
    # Threshold sleep logic for GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL takes 40m between requests,
    # which is too long for certified connectors. Keeping it as documentation for now.
    # "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL": ReportRateLimits(threshold=12, period_in_minutes=480),
    "GET_AFN_INVENTORY_DATA": ReportRateLimits(threshold=2, period_in_minutes=25),
    "GET_FBA_ESTIMATED_FBA_FEES_TXT_DATA": ReportRateLimits(threshold=2000, period_in_minutes=60),
}


def threshold_period_decorator(func):
    def wrapped(*args, **kwargs):
        stream_instance = args[0]
        stream_rate_limits = STREAM_THRESHOLD_PERIOD.get(stream_instance.name)

        # Enable sleeping if stream has known threshold and period or reading without sleeping
        if stream_instance.wait_to_avoid_fatal_errors and stream_rate_limits:
            LOGGER.log(
                LOG_LEVEL,
                f"Stream {stream_instance.name} has a known rate limits values, applying to avoid rate limits.",
            )

            for record in func(*args, **kwargs):
                yield record

                LOGGER.log(LOG_LEVEL, f"Sleeping {stream_rate_limits.wait_time_in_seconds} seconds due to rate limits.")
                time.sleep(stream_rate_limits.wait_time_in_seconds)
        else:
            yield from func(*args, **kwargs)

    return wrapped
