#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Type

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
    )

    level: str = Field(title="Level", description="Chosen level for API", default="ad", enum=["ad", "adset", "campaign", "account"])

    fields: Optional[List[ValidFields]] = Field(
        title="Fields",
        default=[],
    )

    breakdowns: Optional[List[ValidBreakdowns]] = Field(
        title="Breakdowns",
        default=[],
    )

    action_breakdowns: Optional[List[ValidActionBreakdowns]] = Field(
        title="Action Breakdowns",
        default=[],
    )

    time_increment: Optional[PositiveInt] = Field(
        title="Time Increment",
        description="The field is a time interval in days to calucate statistics. We will split the sync into N-days time frames, where N is the number of defined in this field.",
        exclusiveMaximum=90,
        default=1,
    )

    start_date: Optional[datetime] = Field(
        title="Start Date",
        pattern=DATE_TIME_PATTERN,
        examples=["2017-01-25T00:00:00Z"],
    )

    end_date: Optional[datetime] = Field(
        title="End Date",
        description="The field is the date until which to pull data. If not specified, we will use the latest data available.",
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

        @staticmethod
        def schema_extra(schema: Dict[str, Any], model: Type["ConnectorConfig"]) -> None:
            schema["properties"]["end_date"].pop("format")

    access_token: str = Field(
        title="Access Token",
        order=0,
        airbyte_secret=True,
    )

    account_id: str = Field(
        title="Account ID",
        order=1,
        examples=["111111111111111"],
    )

    start_date: datetime = Field(
        title="Start Date",
        order=2,
        pattern=DATE_TIME_PATTERN,
        examples=["2017-01-25T00:00:00Z"],
    )

    end_date: Optional[datetime] = Field(
        title="End Date",
        description="The field is the date until which to pull data. If not specified,  we will use the latest data available.",
        order=3,
        pattern=EMPTY_PATTERN + "|" + DATE_TIME_PATTERN,
        examples=["2017-01-26T00:00:00Z"],
        default_factory=lambda: datetime.now(tz=timezone.utc),
    )

    include_deleted: bool = Field(
        title="Include Deleted Campaigns, Ads, and AdSets",
        order=4,
        default=False,
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
        default=500,
    )

    insights_lookback_window: Optional[PositiveInt] = Field(
        title="Insights Lookback Window",
        order=8,
        maximum=28,
        mininum=1,
        default=28,
    )

    max_batch_size: Optional[PositiveInt] = Field(
        title="Maximum size of Batched Requests",
        order=9,
        default=50,
        maximum=50,
    )

    action_breakdowns_allow_empty: bool = Field(
        description="Allows action_breakdowns to be an empty list",
        default=True,
        airbyte_hidden=True,
    )
