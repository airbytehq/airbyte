#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime
from enum import Enum
from typing import List, Optional

import pendulum
from airbyte_cdk.sources.config import BaseConfig
from facebook_business.adobjects.adsinsights import AdsInsights
from pydantic import BaseModel, Field

logger = logging.getLogger("airbyte")


ValidFields = Enum("ValidEnums", AdsInsights.Field.__dict__)
ValidBreakdowns = Enum("ValidBreakdowns", AdsInsights.Breakdowns.__dict__)
ValidActionBreakdowns = Enum("ValidActionBreakdowns", AdsInsights.ActionBreakdowns.__dict__)


class InsightConfig(BaseModel):
    """Config for custom insights"""

    name: str = Field(description="The name value of insight")
    fields: Optional[List[ValidFields]] = Field(description="A list of chosen fields for fields parameter", default=[])
    breakdowns: Optional[List[ValidBreakdowns]] = Field(description="A list of chosen breakdowns for breakdowns", default=[])
    action_breakdowns: Optional[List[ValidActionBreakdowns]] = Field(
        description="A list of chosen action_breakdowns for action_breakdowns", default=[]
    )


class ConnectorConfig(BaseConfig):
    """Connector config"""

    class Config:
        title = "Source Facebook Marketing"

    start_date: datetime = Field(
        title="Start Date",
        order=0,
        description=(
            "The date from which you'd like to replicate data for all incremental streams, "
            "in the format YYYY-MM-DDT00:00:00Z. All data generated after this date will be replicated."
        ),
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        examples=["2017-01-25T00:00:00Z"],
    )

    end_date: Optional[datetime] = Field(
        title="End Date",
        order=1,
        description=(
            "The date until which you'd like to replicate data for all incremental streams, in the format YYYY-MM-DDT00:00:00Z. "
            "All data generated between start_date and this date will be replicated. "
            "Not setting this option will result in always syncing the latest data."
        ),
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        examples=["2017-01-26T00:00:00Z"],
        default_factory=pendulum.now,
    )

    account_id: str = Field(
        title="Account ID",
        order=2,
        description="The Facebook Ad account ID to use when pulling data from the Facebook Marketing API.",
        examples=["111111111111111"],
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
