# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


from datetime import date
from enum import Enum
from typing import List, Optional

from airbyte_cdk.sources.config import BaseConfig
from pydantic.v1 import Field


class StateFilterEnum(str, Enum):
    enabled = "enabled"
    paused = "paused"
    archived = "archived"


class ReportRecordTypeEnum(str, Enum):
    adGroups = "adGroups"
    asins = "asins"
    asins_keywords = "asins_keywords"
    asins_targets = "asins_targets"
    campaigns = "campaigns"
    keywords = "keywords"
    productAds = "productAds"
    targets = "targets"


class SourceAmazonAdsSpec(BaseConfig):
    class Config:
        title = "Source Amazon Ads"
        use_enum_values = True

    auth_type: str = Field("oauth2.0", const=True, title="Auth Type", order=0)
    client_id: str = Field(
        ...,
        description='The client ID of your Amazon Ads developer application. See the <a href="https://advertising.amazon.com/API/docs/en-us/get-started/generate-api-tokens#retrieve-your-client-id-and-client-secret">docs</a> for more information.',
        title="Client ID",
        airbyte_secret=True,
        order=1,
    )
    client_secret: str = Field(
        ...,
        description='The client secret of your Amazon Ads developer application. See the <a href="https://advertising.amazon.com/API/docs/en-us/get-started/generate-api-tokens#retrieve-your-client-id-and-client-secret">docs</a> for more information.',
        title="Client Secret",
        airbyte_secret=True,
        order=2,
    )
    refresh_token: str = Field(
        ...,
        description='Amazon Ads refresh token. See the <a href="https://advertising.amazon.com/API/docs/en-us/get-started/generate-api-tokens">docs</a> for more information on how to obtain this token.',
        title="Refresh Token",
        airbyte_secret=True,
        order=3,
    )
    region: Optional[str] = Field(
        "NA",
        description='Region to pull data from (EU/NA/FE). See <a href="https://advertising.amazon.com/API/docs/en-us/info/api-overview#api-endpoints">docs</a> for more details.',
        title="Region",
        enum=["NA", "EU", "FE"],
        order=4,
    )
    start_date: Optional[date] = Field(
        None,
        description="The Start date for collecting reports, should not be more than 60 days in the past. In YYYY-MM-DD format",
        examples=["2022-10-10", "2022-10-22"],
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
        title="Start Date",
        order=5,
    )
    profiles: Optional[List[int]] = Field(
        None,
        description='Profile IDs you want to fetch data for. The Amazon Ads source connector supports only profiles with seller and vendor type, profiles with agency type will be ignored. See <a href="https://advertising.amazon.com/API/docs/en-us/concepts/authorization/profiles">docs</a> for more details. Note: If Marketplace IDs are also selected, profiles will be selected if they match the Profile ID OR the Marketplace ID.',
        title="Profile IDs",
        order=6,
    )
    marketplace_ids: Optional[List[str]] = Field(
        None,
        description="Marketplace IDs you want to fetch data for. Note: If Profile IDs are also selected, profiles will be selected if they match the Profile ID OR the Marketplace ID.",
        title="Marketplace IDs",
        order=7,
    )
    state_filter: Optional[List[StateFilterEnum]] = Field(
        default=[],
        description="Reflects the state of the Display, Product, and Brand Campaign streams as enabled, paused, or archived. If you do not populate this field, it will be ignored completely.",
        title="State Filter",
        unique_items=True,
        order=8,
    )
    look_back_window: Optional[int] = Field(
        3,
        description="The amount of days to go back in time to get the updated data from Amazon Ads",
        examples=[3, 10],
        title="Look Back Window",
        order=9,
    )
    report_record_types: Optional[List[ReportRecordTypeEnum]] = Field(
        [],
        description='Optional configuration which accepts an array of string of record types. Leave blank for default behaviour to pull all report types. Use this config option only if you want to pull specific report type(s). See <a href="https://advertising.amazon.com/API/docs/en-us/reporting/v2/report-types">docs</a> for more details',
        title="Report Record Types",
        unique_items=True,
        order=10,
    )
