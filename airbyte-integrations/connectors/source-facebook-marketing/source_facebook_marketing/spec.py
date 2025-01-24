#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import List, Literal, Optional, Set, Union

from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.adobjects.campaign import Campaign
from pydantic.v1 import BaseModel, Field, PositiveInt, constr

from airbyte_cdk.sources.config import BaseConfig
from airbyte_cdk.utils.oneof_option_config import OneOfOptionConfig


logger = logging.getLogger("airbyte")


# Those fields were removed as there were causing `Tried accessing nonexisting field on node type` error from Meta
# For more information, see https://github.com/airbytehq/airbyte/pull/38860
_REMOVED_FIELDS = ["conversion_lead_rate", "cost_per_conversion_lead", "adset_start"]
adjusted_ads_insights_fields = {key: value for key, value in AdsInsights.Field.__dict__.items() if key not in _REMOVED_FIELDS}
ValidFields = Enum("ValidEnums", adjusted_ads_insights_fields)

ValidBreakdowns = Enum("ValidBreakdowns", AdsInsights.Breakdowns.__dict__)
ValidActionBreakdowns = Enum("ValidActionBreakdowns", AdsInsights.ActionBreakdowns.__dict__)
ValidCampaignStatuses = Enum("ValidCampaignStatuses", Campaign.EffectiveStatus.__dict__)
ValidAdSetStatuses = Enum("ValidAdSetStatuses", AdSet.EffectiveStatus.__dict__)
ValidAdStatuses = Enum("ValidAdStatuses", Ad.EffectiveStatus.__dict__)
DATE_TIME_PATTERN = "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"
EMPTY_PATTERN = "^$"


class OAuthCredentials(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Authenticate via Facebook Marketing (Oauth)"
        discriminator = "auth_type"

    auth_type: Literal["Client"] = Field("Client", const=True)
    client_id: str = Field(
        title="Client ID",
        description="Client ID for the Facebook Marketing API",
        airbyte_secret=True,
    )
    client_secret: str = Field(
        title="Client Secret",
        description="Client Secret for the Facebook Marketing API",
        airbyte_secret=True,
    )
    access_token: Optional[str] = Field(
        title="Access Token",
        description="The value of the generated access token. "
        'From your App’s Dashboard, click on "Marketing API" then "Tools". '
        'Select permissions <b>ads_management, ads_read, read_insights, business_management</b>. Then click on "Get token". '
        'See the <a href="https://docs.airbyte.com/integrations/sources/facebook-marketing">docs</a> for more information.',
        airbyte_secret=True,
    )


class ServiceAccountCredentials(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Service Account Key Authentication"
        discriminator = "auth_type"

    auth_type: Literal["Service"] = Field("Service", const=True)
    access_token: str = Field(
        title="Access Token",
        description="The value of the generated access token. "
        'From your App’s Dashboard, click on "Marketing API" then "Tools". '
        'Select permissions <b>ads_management, ads_read, read_insights, business_management</b>. Then click on "Get token". '
        'See the <a href="https://docs.airbyte.com/integrations/sources/facebook-marketing">docs</a> for more information.',
        airbyte_secret=True,
    )


class InsightConfig(BaseModel):
    """Config for custom insights"""

    class Config:
        use_enum_values = True

    name: str = Field(
        title="Name",
        description="The name value of insight",
    )

    level: str = Field(
        title="Level",
        description="Chosen level for API",
        default="ad",
        enum=["ad", "adset", "campaign", "account"],
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

    action_report_time: str = Field(
        title="Action Report Time",
        description=(
            "Determines the report time of action stats. For example, if a person saw the ad on Jan 1st "
            "but converted on Jan 2nd, when you query the API with action_report_time=impression, you see a conversion on Jan 1st. "
            "When you query the API with action_report_time=conversion, you see a conversion on Jan 2nd."
        ),
        default="mixed",
        enum=["conversion", "impression", "mixed"],
    )

    time_increment: Optional[PositiveInt] = Field(
        title="Time Increment",
        description=(
            "Time window in days by which to aggregate statistics. The sync will be chunked into N day intervals, where N is the number of days you specified. "
            "For example, if you set this value to 7, then all statistics will be reported as 7-day aggregates by starting from the start_date. If the start and end dates are October 1st and October 30th, then the connector will output 5 records: 01 - 06, 07 - 13, 14 - 20, 21 - 27, and 28 - 30 (3 days only). "
            "The minimum allowed value for this field is 1, and the maximum is 89."
        ),
        maximum=89,
        minimum=1,
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
    insights_job_timeout: Optional[PositiveInt] = Field(
        title="Custom Insights Job Timeout",
        description="The insights job timeout",
        maximum=60,
        mininum=10,
        default=60,
    )


class ConnectorConfig(BaseConfig):
    """Connector config"""

    class Config:
        title = "Source Facebook Marketing"
        use_enum_values = True

    account_ids: Set[constr(regex="^[0-9]+$")] = Field(
        title="Ad Account ID(s)",
        order=0,
        description=(
            "The Facebook Ad account ID(s) to pull data from. "
            "The Ad account ID number is in the account dropdown menu or in your browser's address "
            'bar of your <a href="https://adsmanager.facebook.com/adsmanager/">Meta Ads Manager</a>. '
            'See the <a href="https://www.facebook.com/business/help/1492627900875762">docs</a> for more information.'
        ),
        pattern_descriptor="The Ad Account ID must be a number.",
        examples=["111111111111111"],
        min_items=1,
    )

    access_token: Optional[str] = Field(
        title="Access Token",
        order=1,
        description=(
            "The value of the generated access token. "
            'From your App’s Dashboard, click on "Marketing API" then "Tools". '
            'Select permissions <b>ads_management, ads_read, read_insights, business_management</b>. Then click on "Get token". '
            'See the <a href="https://docs.airbyte.com/integrations/sources/facebook-marketing">docs</a> for more information.'
        ),
        airbyte_secret=True,
    )

    credentials: Union[OAuthCredentials, ServiceAccountCredentials] = Field(
        title="Authentication",
        description="Credentials for connecting to the Facebook Marketing API",
        type="object",
    )

    start_date: Optional[datetime] = Field(
        title="Start Date",
        order=2,
        description=(
            "The date from which you'd like to replicate data for all incremental streams, "
            "in the format YYYY-MM-DDT00:00:00Z. If not set then all data will be replicated for usual streams and only last 2 years for insight streams."
        ),
        pattern=DATE_TIME_PATTERN,
        examples=["2017-01-25T00:00:00Z"],
    )

    end_date: Optional[datetime] = Field(
        title="End Date",
        order=3,
        description=(
            "The date until which you'd like to replicate data for all incremental streams, in the format YYYY-MM-DDT00:00:00Z."
            " All data generated between the start date and this end date will be replicated. "
            "Not setting this option will result in always syncing the latest data."
        ),
        pattern=EMPTY_PATTERN + "|" + DATE_TIME_PATTERN,
        examples=["2017-01-26T00:00:00Z"],
        default_factory=lambda: datetime.now(tz=timezone.utc),
    )

    campaign_statuses: Optional[List[ValidCampaignStatuses]] = Field(
        title="Campaign Statuses",
        order=4,
        description="Select the statuses you want to be loaded in the stream. If no specific statuses are selected, the API's default behavior applies, and some statuses may be filtered out.",
        default=[],
    )

    adset_statuses: Optional[List[ValidAdSetStatuses]] = Field(
        title="AdSet Statuses",
        order=5,
        description="Select the statuses you want to be loaded in the stream. If no specific statuses are selected, the API's default behavior applies, and some statuses may be filtered out.",
        default=[],
    )

    ad_statuses: Optional[List[ValidAdStatuses]] = Field(
        title="Ad Statuses",
        order=6,
        description="Select the statuses you want to be loaded in the stream. If no specific statuses are selected, the API's default behavior applies, and some statuses may be filtered out.",
        default=[],
    )

    fetch_thumbnail_images: bool = Field(
        title="Fetch Thumbnail Images from Ad Creative",
        order=7,
        default=False,
        description="Set to active if you want to fetch the thumbnail_url and store the result in thumbnail_data_url for each Ad Creative.",
    )

    custom_insights: Optional[List[InsightConfig]] = Field(
        title="Custom Insights",
        order=8,
        description=(
            "A list which contains ad statistics entries, each entry must have a name and can contains fields, "
            'breakdowns or action_breakdowns. Click on "add" to fill this field.'
        ),
    )

    page_size: Optional[PositiveInt] = Field(
        title="Page Size of Requests",
        order=10,
        default=100,
        description=(
            "Page size used when sending requests to Facebook API to specify number of records per page when response has pagination. "
            "Most users do not need to set this field unless they specifically need to tune the connector to address specific issues or use cases."
        ),
    )

    insights_lookback_window: Optional[PositiveInt] = Field(
        title="Insights Lookback Window",
        order=11,
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

    insights_job_timeout: Optional[PositiveInt] = Field(
        title="Insights Job Timeout",
        order=12,
        description=(
            "Insights Job Timeout establishes the maximum amount of time (in minutes) of waiting for the report job to complete. "
            "When timeout is reached the job is considered failed and we are trying to request smaller amount of data by breaking the job to few smaller ones. "
            "If you definitely know that 60 minutes is not enough for your report to be processed then you can decrease the timeout value, "
            "so we start breaking job to smaller parts faster."
        ),
        maximum=60,
        mininum=10,
        default=60,
    )
    
    use_account_attribution_setting: bool = Field(
        title="Use Account Attribution Setting",
        order=13,
        default=False,
        description="When this parameter is set to true, your ads results are shown using the attribution settings defined for the ad account",
    )
    
    use_unified_attribution_setting: bool = Field(
        title="Use Unified Attribution Setting",
        order=14,
        default=False,
        description="When this parameter is set to true, your ads results will be shown using unified attribution settings defined at ad set level and parameter use_account_attribution_setting will be ignored. Note: Please set this to true to get the same behavior as in the Ads Manager.",
    )

    action_breakdowns_allow_empty: bool = Field(
        description="Allows action_breakdowns to be an empty list",
        default=True,
        airbyte_hidden=True,
    )

    client_id: Optional[str] = Field(
        description="The Client Id for your OAuth app",
        airbyte_secret=True,
        airbyte_hidden=True,
    )

    client_secret: Optional[str] = Field(
        description="The Client Secret for your OAuth app",
        airbyte_secret=True,
        airbyte_hidden=True,
    )
