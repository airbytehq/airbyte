#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime
from enum import Enum
from typing import List, Optional

import pendulum
from airbyte_cdk.sources.config import BaseConfig
from facebook_business.adobjects.adsinsights import AdsInsights
from pydantic import BaseModel, Field, PositiveInt

logger = logging.getLogger("airbyte")


ValidFields = Enum("ValidEnums", AdsInsights.Field.__dict__)
ValidBreakdowns = Enum("ValidBreakdowns", AdsInsights.Breakdowns.__dict__)
ValidActionBreakdowns = Enum("ValidActionBreakdowns", AdsInsights.ActionBreakdowns.__dict__)
DATE_TIME_PATTERN = "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"


class InsightConfig(BaseModel):
    """Config for custom insights"""

    class Config:
        use_enum_values = True

    name: str = Field(
        title="Name",
        description="The name value of insight",
    )

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
            "All data generated between the start date and this date will be replicated. "
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
        description="The Facebook Ad account ID to use when pulling data from the Facebook Marketing API.",
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
            "The date until which you'd like to replicate data for all incremental streams, in the format YYYY-MM-DDT00:00:00Z. "
            "All data generated between start_date and this date will be replicated. "
            "Not setting this option will result in always syncing the latest data."
        ),
        pattern=DATE_TIME_PATTERN,
        examples=["2017-01-26T00:00:00Z"],
        default_factory=pendulum.now,
    )

    access_token: str = Field(
        title="Access Token",
        order=3,
        description=(
            "The value of the access token generated. "
            'See the <a href="https://docs.airbyte.io/integrations/sources/facebook-marketing">docs</a> for more information'
        ),
        airbyte_secret=True,
    )

    include_deleted: bool = Field(
        title="Include Deleted",
        order=4,
        default=False,
        description="Include data from deleted Campaigns, Ads, and AdSets",
    )

    fetch_thumbnail_images: bool = Field(
        title="Fetch Thumbnail Images",
        order=5,
        default=False,
        description="In each Ad Creative, fetch the thumbnail_url and store the result in thumbnail_data_url",
    )

    custom_insights: Optional[List[InsightConfig]] = Field(
        title="Custom Insights",
        order=6,
        description=(
            "A list which contains insights entries, each entry must have a name and can contains fields, breakdowns or action_breakdowns)"
        ),
    )

    page_size: Optional[PositiveInt] = Field(
        title="Page Size of Requests",
        order=7,
        default=100,
        description=(
            "Page size used when sending requests to Facebook API to specify number of records per page when response has pagination. Most users do not need to set this field unless they specifically need to tune the connector to address specific issues or use cases."
        ),
    )

    insights_lookback_window: Optional[PositiveInt] = Field(
        title="Insights Lookback Window",
        order=8,
        description="The attribution window",
        maximum=28,
        mininum=1,
        default=28,
    )

    max_batch_size: Optional[PositiveInt] = Field(
        title="Maximum size of Batched Requests",
        order=9,
        description="Maximum batch size used when sending batch requests to Facebook API. Most users do not need to set this field unless they specifically need to tune the connector to address specific issues or use cases.",
        default=50,
    )
