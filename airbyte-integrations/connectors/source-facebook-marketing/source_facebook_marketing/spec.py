#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from typing import List, Optional

import pendulum
from pydantic import BaseModel, Field

from .common import get_default_fields_and_breakdowns

default_fields, default_breakdowns, default_action_breakdowns = get_default_fields_and_breakdowns()


class InsightConfig(BaseModel):

    name: str = Field(description="The name value of insight", order=1)

    fields: Optional[List[str]] = Field(
        description="A list of chosen fields for fields parameter", default=[], enum=default_fields, order=2
    )

    breakdowns: Optional[List[str]] = Field(
        description="A list of chosen breakdowns for breakdowns", default=[], order=3, enum=default_breakdowns
    )

    action_breakdowns: Optional[List[str]] = Field(
        description="A list of chosen action_breakdowns for action_breakdowns", default=[], order=4, enum=default_action_breakdowns
    )

    time_increment: Optional[str] = Field(
        description='Time window to aggregate statistic for certain period of time, could be either "monthly" or integer number from 1 to 90 ',
        pattern="^(monthly)|([0-9]{1,2})$",
        default=["1"],
        order=5,
    )


class ConnectorConfig(BaseModel):
    class Config:
        title = "Source Facebook Marketing"

    account_id: str = Field(description="The Facebook Ad account ID to use when pulling data from the Facebook Marketing API.")

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

    include_deleted: bool = Field(default=False, description="Include data from deleted campaigns, ads, and adsets")

    insights_lookback_window: int = Field(
        default=28,
        description="The attribution window for the actions",
        minimum=0,
        maximum=28,
    )

    insights_days_per_job: int = Field(
        default=7,
        description="Number of days to sync in one job (the more data you have, the smaller this parameter should be)",
        minimum=1,
        maximum=30,
    )
    custom_insights: Optional[List[InsightConfig]] = Field(
        description="A list wich contains insights entries, each entry must have a name and can contains fields, breakdowns or action_breakdowns)"
    )
