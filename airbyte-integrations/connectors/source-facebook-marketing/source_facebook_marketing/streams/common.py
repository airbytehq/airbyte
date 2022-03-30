#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import http.client
import logging
import sys
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Union

import backoff
import pendulum
from airbyte_cdk.sources.config import BaseConfig
from facebook_business.exceptions import FacebookRequestError
from pydantic import Field

# The Facebook API error codes indicating rate-limiting are listed at
# https://developers.facebook.com/docs/graph-api/overview/rate-limiting/
FACEBOOK_RATE_LIMIT_ERROR_CODES = (4, 17, 32, 613, 80000, 80001, 80002, 80003, 80004, 80005, 80006, 80008)
FACEBOOK_TEMPORARY_OAUTH_ERROR_CODE = 2
FACEBOOK_BATCH_ERROR_CODE = 960
FACEBOOK_UNKNOWN_ERROR_CODE = 99
FACEBOOK_CONNECTION_RESET_ERROR_CODE = 104
DEFAULT_SLEEP_INTERVAL = pendulum.duration(minutes=1)
MAX_BATCH_SIZE = 50

logger = logging.getLogger("airbyte")


class AccountSelectionStrategyEnum(str, Enum):
    all = "all"
    subset = "subset"


class AccountSelectionStrategyAll(BaseConfig):
    """Fetch data for all available accounts."""

    class Config:
        title = "All accounts assigned to your user"

    selection_strategy: str = Field(default=AccountSelectionStrategyEnum.all, const=AccountSelectionStrategyEnum.all)


class AccountSelectionStrategySubset(BaseConfig):
    """Fetch data for subset of account ids."""

    class Config:
        title = "Subset of your accounts"

    selection_strategy: str = Field(default=AccountSelectionStrategyEnum.subset, const=AccountSelectionStrategyEnum.subset)
    ids: List[str] = Field(title="IDs", description="List of accounts from which data will be fetched", min_items=1, uniqueItems=True)


class InsightConfig(BaseConfig):

    name: str = Field(description="The name value of insight")

    fields: Optional[List[str]] = Field(description="A list of chosen fields for fields parameter", default=[])

    breakdowns: Optional[List[str]] = Field(description="A list of chosen breakdowns for breakdowns", default=[])

    action_breakdowns: Optional[List[str]] = Field(description="A list of chosen action_breakdowns for action_breakdowns", default=[])


class ConnectorConfig(BaseConfig):
    class Config:
        title = "Source Facebook Marketing"

    accounts: Union[AccountSelectionStrategyAll, AccountSelectionStrategySubset] = Field(
        description="The Facebook Ad account ID to use when pulling data from the Facebook Marketing API."
    )

    access_token: str = Field(
        description='The value of the access token generated. See the <a href="https://docs.airbyte.io/integrations/sources/facebook-marketing">docs</a> for more information',
        airbyte_secret=True,
    )

    start_date: datetime = Field(
        description="The date from which you'd like to replicate data for AdCreatives and AdInsights APIs, in the format YYYY-MM-DDT00:00:00Z. All data generated after this date will be replicated.",
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        examples=["2017-01-25T00:00:00Z"],
    )

    end_date: Optional[datetime] = Field(
        description="The date until which you'd like to replicate data for AdCreatives and AdInsights APIs, in the format YYYY-MM-DDT00:00:00Z. All data generated between start_date and this date will be replicated. Not setting this option will result in always syncing the latest data.",
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        examples=["2017-01-26T00:00:00Z"],
        default_factory=pendulum.now,
    )

    fetch_thumbnail_images: bool = Field(
        default=False, description="In each Ad Creative, fetch the thumbnail_url and store the result in thumbnail_data_url"
    )

    include_deleted: bool = Field(default=False, description="Include data from deleted campaigns, ads, and adsets.")

    insights_lookback_window: int = Field(
        default=28,
        description="The attribution window for the actions",
        minimum=0,
        maximum=28,
    )

    insights_days_per_job: int = Field(
        default=7,
        description="Number of days to sync in one job. The more data you have - the smaller you want this parameter to be.",
        minimum=1,
        maximum=30,
    )
    custom_insights: Optional[List[InsightConfig]] = Field(
        description="A list wich contains insights entries, each entry must have a name and can contains fields, breakdowns or action_breakdowns)"
    )

    @property
    def account_selection_strategy(self):
        return self.accounts.selection_strategy

    @property
    def account_selection_strategy_is_all(self):
        return self.account_selection_strategy == AccountSelectionStrategyEnum.all

    @property
    def account_selection_strategy_is_subset(self):
        return self.account_selection_strategy == AccountSelectionStrategyEnum.subset


class FacebookAPIException(Exception):
    """General class for all API errors"""


class JobException(Exception):
    """Scheduled job failed"""


def retry_pattern(backoff_type, exception, **wait_gen_kwargs):
    def log_retry_attempt(details):
        _, exc, _ = sys.exc_info()
        logger.info(str(exc))
        logger.info(f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} more seconds then retrying...")

    def should_retry_api_error(exc):
        if isinstance(exc, FacebookRequestError):
            call_rate_limit_error = exc.api_error_code() in FACEBOOK_RATE_LIMIT_ERROR_CODES
            temporary_oauth_error = exc.api_error_code() == FACEBOOK_TEMPORARY_OAUTH_ERROR_CODE
            batch_timeout_error = exc.http_status() == http.client.BAD_REQUEST and exc.api_error_code() == FACEBOOK_BATCH_ERROR_CODE
            unknown_error = exc.api_error_subcode() == FACEBOOK_UNKNOWN_ERROR_CODE
            connection_reset_error = exc.api_error_code() == FACEBOOK_CONNECTION_RESET_ERROR_CODE
            server_error = exc.http_status() == http.client.INTERNAL_SERVER_ERROR
            return any(
                (
                    exc.api_transient_error(),
                    unknown_error,
                    call_rate_limit_error,
                    batch_timeout_error,
                    connection_reset_error,
                    temporary_oauth_error,
                    server_error,
                )
            )
        return True

    return backoff.on_exception(
        backoff_type,
        exception,
        jitter=None,
        on_backoff=log_retry_attempt,
        giveup=lambda exc: not should_retry_api_error(exc),
        **wait_gen_kwargs,
    )


def deep_merge(a: Any, b: Any) -> Any:
    """Merge two values, with `b` taking precedence over `a`."""
    if isinstance(a, dict) and isinstance(b, dict):
        # set of all keys in both dictionaries
        keys = set(a.keys()) | set(b.keys())

        return {key: deep_merge(a.get(key), b.get(key)) for key in keys}
    elif isinstance(a, list) and isinstance(b, list):
        return [*a, *b]
    elif isinstance(a, set) and isinstance(b, set):
        return a | b
    else:
        return a if b is None else b
