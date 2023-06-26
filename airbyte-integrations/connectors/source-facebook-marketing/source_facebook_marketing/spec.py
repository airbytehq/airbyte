#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from airbyte_cdk.sources.config import BaseConfig
from facebook_business.adobjects.adsinsights import AdsInsights
from pydantic import BaseModel, Field, PositiveInt

logger = logging.getLogger("airbyte")


ValidFields = Enum("ValidEnums", AdsInsights.Field.__dict__)
ValidBreakdowns = Enum("ValidBreakdowns", AdsInsights.Breakdowns.__dict__)
ValidActionBreakdowns = Enum("ValidActionBreakdowns", AdsInsights.ActionBreakdowns.__dict__)
DATE_TIME_PATTERN = "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"
EMPTY_PATTERN = "^$"


class InsightConfig(BaseModel):
    """Config for custom insights"""

    class Config:
        use_enum_values = True

    name: str = Field(
        title="Name",
        description="The name value of insight",
    )

    level: str = Field(title="Level", description="Chosen level for API", default="ad", enum=["ad", "adset", "campaign", "account"])

    fields: Optional[List[ValidFields]] = Field(
        title="Fields",
        description="A list of chosen fields for fields parameter",
        default=[],
    )

    breakdowns: Optional[List[ValidBreakdowns]] = Field(
        title="Breakdowns",
        description="A list of chosen breakdowns for breakdowns",
        default=[],
    )

    action_breakdowns: Optional[List[ValidActionBreakdowns]] = Field(
        title="Action Breakdowns",
        description="A list of chosen action_breakdowns for action_breakdowns",
        default=[],
    )

    time_increment: Optional[PositiveInt] = Field(
        title="Time Increment",
        description=(
            "Time window in days by which to aggregate statistics. The sync will be chunked into N day intervals, where N is the number of days you specified. "
            "For example, if you set this value to 7, then all statistics will be reported as 7-day aggregates by starting from the start_date. If the start and end dates are October 1st and October 30th, then the connector will output 5 records: 01 - 06, 07 - 13, 14 - 20, 21 - 27, and 28 - 30 (3 days only)."
        ),
        exclusiveMaximum=90,
        default=1,
    )

    start_date: Optional[datetime] = Field(
        title="Start Date",
        description="The date from which you'd like to replicate data for this stream, in the format YYYY-MM-DDT00:00:00Z.",
        pattern=DATE_TIME_PATTERN,
        examples=["2017-01-25T00:00:00Z"],
    )

    end_date: Optional[datetime] = Field(
        title="End Date",
        description=(
            "The date until which you'd like to replicate data for this stream, in the format YYYY-MM-DDT00:00:00Z. "
            "All data generated between the start date and this end date will be replicated. "
            "Not setting this option will result in always syncing the latest data."
        ),
        pattern=DATE_TIME_PATTERN,
        examples=["2017-01-26T00:00:00Z"],
    )
    insights_lookback_window: Optional[PositiveInt] = Field(
        title="Custom Insights Lookback Window",
        description="The attribution window",
        maximum=28,
        mininum=1,
        default=28,
    )


class ConnectorConfig(BaseConfig):
    """Connector config"""

    class Config:
        title = "Source Facebook Marketing"

    account_id: str = Field(
        title="Account ID",
        order=0,
        description=(
            "The Facebook Ad account ID to use when pulling data from the Facebook Marketing API."
            " Open your Meta Ads Manager. The Ad account ID number is in the account dropdown menu or in your browser's address bar. "
            'See the <a href="https://www.facebook.com/business/help/1492627900875762">docs</a> for more information.'
        ),
        pattern="^[0-9]+$",
        pattern_descriptor="1234567890",
        examples=["111111111111111"],
    )

    start_date: datetime = Field(
        title="Start Date",
        order=1,
        description=(
            "The date from which you'd like to replicate data for all incremental streams, "
            "in the format YYYY-MM-DDT00:00:00Z. All data generated after this date will be replicated."
        ),
        pattern=DATE_TIME_PATTERN,
        examples=["2017-01-25T00:00:00Z"],
    )

    end_date: Optional[datetime] = Field(
        title="End Date",
        order=2,
        description=(
            "The date until which you'd like to replicate data for all incremental streams, in the format YYYY-MM-DDT00:00:00Z."
            " All data generated between the start date and this end date will be replicated. "
            "Not setting this option will result in always syncing the latest data."
        ),
        pattern=EMPTY_PATTERN + "|" + DATE_TIME_PATTERN,
        examples=["2017-01-26T00:00:00Z"],
        default_factory=lambda: datetime.now(tz=timezone.utc),
    )

    access_token: str = Field(
        title="Access Token",
        order=3,
        description=(
            "The value of the generated access token. "
            'From your App’s Dashboard, click on "Marketing API" then "Tools". '
            'Select permissions <b>ads_management, ads_read, read_insights, business_management</b>. Then click on "Get token". '
            'See the <a href="https://docs.airbyte.com/integrations/sources/facebook-marketing">docs</a> for more information.'
        ),
        airbyte_secret=True,
    )

    include_deleted: bool = Field(
        title="Include Deleted Campaigns, Ads, and AdSets",
        order=4,
        default=False,
        description="Set to active if you want to include data from deleted Campaigns, Ads, and AdSets.",
    )

    fetch_thumbnail_images: bool = Field(
        title="Fetch Thumbnail Images from Ad Creative",
        order=5,
        default=False,
        description="Set to active if you want to fetch the thumbnail_url and store the result in thumbnail_data_url for each Ad Creative.",
    )

    custom_insights: Optional[List[InsightConfig]] = Field(
        title="Custom Insights",
        order=6,
        description=(
            "A list which contains ad statistics entries, each entry must have a name and can contains fields, "
            'breakdowns or action_breakdowns. Click on "add" to fill this field.'
        ),
    )

    page_size: Optional[PositiveInt] = Field(
        title="Page Size of Requests",
        order=7,
        default=100,
        description=(
            "Page size used when sending requests to Facebook API to specify number of records per page when response has pagination. "
            "Most users do not need to set this field unless they specifically need to tune the connector to address specific issues or use cases."
        ),
    )

    insights_lookback_window: Optional[PositiveInt] = Field(
        title="Insights Lookback Window",
        order=8,
        description=(
            "The attribution window. Facebook freezes insight data 28 days after it was generated, "
            "which means that all data from the past 28 days may have changed since we last emitted it, "
            "so you can retrieve refreshed insights from the past by setting this parameter. "
            "If you set a custom lookback window value in Facebook account, please provide the same value here."
        ),
        maximum=28,
        mininum=1,
        default=28,
    )

    max_batch_size: Optional[PositiveInt] = Field(
        title="Maximum size of Batched Requests",
        order=9,
        description=(
            "Maximum batch size used when sending batch requests to Facebook API. "
            "Most users do not need to set this field unless they specifically need to tune the connector to address specific issues or use cases."
        ),
        default=50,
    )

    action_breakdowns_allow_empty: bool = Field(
        description="Allows action_breakdowns to be an empty list",
        default=True,
        airbyte_hidden=True,
    )
