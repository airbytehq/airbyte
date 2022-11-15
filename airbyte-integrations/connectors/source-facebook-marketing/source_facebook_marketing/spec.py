#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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

    account_id: str = Field(
        title="Account ID",
        order=0,
        examples=["111111111111111"],
    )

    start_date: datetime = Field(
        title="Start Date",
        order=1,
        pattern=DATE_TIME_PATTERN,
        examples=["2017-01-25T00:00:00Z"],
    )

    end_date: Optional[datetime] = Field(
        title="End Date",
        description="The field is the date until which to pull data. If not specified,  we will use the latest data available.",
        order=2,
        pattern=EMPTY_PATTERN + "|" + DATE_TIME_PATTERN,
        examples=["2017-01-26T00:00:00Z"],
        default_factory=lambda: datetime.now(tz=timezone.utc),
    )

    access_token: str = Field(
        title="Access Token",
        order=3,
        airbyte_secret=True,
    )

    include_deleted: bool = Field(
        title="Include Deleted",
        order=4,
        default=False,
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
    )
