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
<<<<<<< HEAD
        description="The field is the date until which to pull data. If not specified, we will use the latest data available.",
=======
        description=(
            "The date until which you'd like to replicate data for this stream, in the format YYYY-MM-DDT00:00:00Z. "
            "All data generated between the start date and this end date will be replicated. "
            "Not setting this option will result in always syncing the latest data."
        ),
>>>>>>> upstream/master
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
<<<<<<< HEAD
        order=1,
=======
        order=0,
        description=(
            "The Facebook Ad account ID to use when pulling data from the Facebook Marketing API."
            " Open your Meta Ads Manager. The Ad account ID number is in the account dropdown menu or in your browser's address bar. "
            'See the <a href="https://www.facebook.com/business/help/1492627900875762">docs</a> for more information.'
        ),
>>>>>>> upstream/master
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
<<<<<<< HEAD
        description="The field is the date until which to pull data. If not specified,  we will use the latest data available.",
        order=3,
=======
        order=2,
        description=(
            "The date until which you'd like to replicate data for all incremental streams, in the format YYYY-MM-DDT00:00:00Z."
            " All data generated between the start date and this end date will be replicated. "
            "Not setting this option will result in always syncing the latest data."
        ),
>>>>>>> upstream/master
        pattern=EMPTY_PATTERN + "|" + DATE_TIME_PATTERN,
        examples=["2017-01-26T00:00:00Z"],
        default_factory=lambda: datetime.now(tz=timezone.utc),
    )

<<<<<<< HEAD
=======
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

>>>>>>> upstream/master
    include_deleted: bool = Field(
        title="Include Deleted Campaigns, Ads, and AdSets",
        order=4,
        default=False,
<<<<<<< HEAD
=======
        description="Set to active if you want to include data from deleted Campaigns, Ads, and AdSets.",
>>>>>>> upstream/master
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
<<<<<<< HEAD
=======
        description=(
            "Page size used when sending requests to Facebook API to specify number of records per page when response has pagination. "
            "Most users do not need to set this field unless they specifically need to tune the connector to address specific issues or use cases."
        ),
>>>>>>> upstream/master
    )

    insights_lookback_window: Optional[PositiveInt] = Field(
        title="Insights Lookback Window",
        order=8,
<<<<<<< HEAD
=======
        description=(
            "The attribution window. Facebook freezes insight data 28 days after it was generated, "
            "which means that all data from the past 28 days may have changed since we last emitted it, "
            "so you can retrieve refreshed insights from the past by setting this parameter. "
            "If you set a custom lookback window value in Facebook account, please provide the same value here."
        ),
>>>>>>> upstream/master
        maximum=28,
        mininum=1,
        default=28,
    )

    max_batch_size: Optional[PositiveInt] = Field(
        title="Maximum size of Batched Requests",
        order=9,
<<<<<<< HEAD
=======
        description=(
            "Maximum batch size used when sending batch requests to Facebook API. "
            "Most users do not need to set this field unless they specifically need to tune the connector to address specific issues or use cases."
        ),
>>>>>>> upstream/master
        default=50,
    )

    action_breakdowns_allow_empty: bool = Field(
        description="Allows action_breakdowns to be an empty list",
        default=True,
        airbyte_hidden=True,
    )
