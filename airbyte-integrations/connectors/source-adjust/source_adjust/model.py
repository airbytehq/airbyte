#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

# The spec and report schema are generated from this module.
#
# import source_adjust.model, yaml, json
# yaml.dump(yaml.safe_load(source_adjust.model.Spec.schema_json()),
#     stream=open('source_adjust/spec.yaml', 'w'),
# )

import datetime
import decimal
import typing

import pydantic


BASE_METRICS = typing.Literal[
    "network_cost",
    "network_cost_diff",
    "network_clicks",
    "network_impressions",
    "network_installs",
    "network_installs_diff",
    "network_ecpc",
    "network_ecpi",
    "network_ecpm",
    "arpdau_ad",
    "arpdau",
    "arpdau_iap",
    "ad_impressions",
    "ad_rpm",
    "ad_revenue",
    "cohort_ad_revenue",
    "cost",
    "adjust_cost",
    "all_revenue",
    "cohort_all_revenue",
    "daus",
    "maus",
    "waus",
    "base_sessions",
    "ctr",
    "click_conversion_rate",
    "click_cost",
    "clicks",
    "paid_clicks",
    "deattributions",
    "ecpc",
    "gdpr_forgets",
    "gross_profit",
    "cohort_gross_profit",
    "impression_conversion_rate",
    "impression_cost",
    "impressions",
    "paid_impressions",
    "install_cost",
    "installs",
    "paid_installs",
    "installs_per_mile",
    "limit_ad_tracking_installs",
    "limit_ad_tracking_install_rate",
    "limit_ad_tracking_reattribution_rate",
    "limit_ad_tracking_reattributions",
    "non_organic_installs",
    "organic_installs",
    "roas_ad",
    "roas",
    "roas_iap",
    "reattributions",
    "return_on_investment",
    "revenue",
    "cohort_revenue",
    "revenue_events",
    "revenue_to_cost",
    "sessions",
    "events",
    "ecpi_all",
    "ecpi",
    "ecpm",
]


DIMENSIONS = typing.Literal[
    "os_name",
    "device_type",
    "app",
    "app_token",
    "store_id",
    "store_type",
    "app_network",
    "currency",
    "currency_code",
    "network",
    "campaign",
    "campaign_network",
    "campaign_id_network",
    "adgroup",
    "adgroup_network",
    "adgroup_id_network",
    "source_network",
    "source_id_network",
    "creative",
    "creative_network",
    "creative_id_network",
    "country",
    "country_code",
    "region",
    "partner_name",
    "partner_id",
]


class Report(pydantic.BaseModel):
    # Base metrics
    network_cost: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Ad Spend (Network).",
    )

    network_cost_diff: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Ad Spend Diff (Network).",
    )

    network_clicks: typing.Optional[int] = pydantic.Field(
        None,
        description="Clicks (Network).",
    )

    network_impressions: typing.Optional[int] = pydantic.Field(
        None,
        description="Impressions (Network).",
    )

    network_installs: typing.Optional[int] = pydantic.Field(
        None,
        description="Installs (Network).",
    )

    network_installs_diff: typing.Optional[int] = pydantic.Field(
        None,
        description="Installs Diff (Network).",
    )

    network_ecpc: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="eCPC (Network).",
    )

    network_ecpi: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="eCPI (Network).",
    )

    network_ecpm: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="eCPM (Network).",
    )

    arpdau_ad: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="ARPDAU (Ad).",
    )

    arpdau: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="ARPDAU (All).",
    )

    arpdau_iap: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="ARPDAU (IAP).",
    )

    ad_impressions: typing.Optional[int] = pydantic.Field(
        None,
        description="Ad Impressions.",
    )

    ad_rpm: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Ad RPM.",
    )

    ad_revenue: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Ad Revenue.",
    )

    cohort_ad_revenue: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Ad Revenue (Cohort).",
    )

    cost: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Ad Spend.",
    )

    adjust_cost: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Ad Spend (Attribution).",
    )

    all_revenue: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="All Revenue.",
    )

    cohort_all_revenue: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="All Revenue (Cohort).",
    )

    daus: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Avg. DAUs.",
    )

    maus: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Avg. MAUs.",
    )

    waus: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Avg. WAUs.",
    )

    base_sessions: typing.Optional[int] = pydantic.Field(
        None,
        description="Base Sessions.",
    )

    ctr: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="CTR.",
    )

    click_conversion_rate: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Click Conversion Rate (CCR).",
    )

    click_cost: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Click Cost.",
    )

    clicks: typing.Optional[int] = pydantic.Field(
        None,
        description="Clicks.",
    )

    paid_clicks: typing.Optional[int] = pydantic.Field(
        None,
        description="Clicks (paid).",
    )

    deattributions: typing.Optional[int] = pydantic.Field(
        None,
        description="Deattributions.",
    )

    ecpc: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Effective Cost per Click (eCPC).",
    )

    gdpr_forgets: typing.Optional[int] = pydantic.Field(
        None,
        description="GDPR Forgets.",
    )

    gross_profit: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Gross profit.",
    )

    cohort_gross_profit: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Gross profit (Cohort).",
    )

    impression_conversion_rate: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Impression Conversion Rate (ICR).",
    )

    impression_cost: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Impression Cost.",
    )

    impressions: typing.Optional[int] = pydantic.Field(
        None,
        description="Impressions.",
    )

    paid_impressions: typing.Optional[int] = pydantic.Field(
        None,
        description="Impressions (paid).",
    )

    install_cost: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Install Cost.",
    )

    installs: typing.Optional[int] = pydantic.Field(
        None,
        description="Installs.",
    )

    paid_installs: typing.Optional[int] = pydantic.Field(
        None,
        description="Installs (paid).",
    )

    installs_per_mile: typing.Optional[int] = pydantic.Field(
        None,
        description="Installs per Mille (IPM).",
    )

    limit_ad_tracking_installs: typing.Optional[int] = pydantic.Field(
        None,
        description="Limit Ad Tracking Installs.",
    )

    limit_ad_tracking_install_rate: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Limit Ad Tracking Rate.",
    )

    limit_ad_tracking_reattribution_rate: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Limit Ad Tracking Reattribution Rate.",
    )

    limit_ad_tracking_reattributions: typing.Optional[int] = pydantic.Field(
        None,
        description="Limit Ad Tracking Reattributions.",
    )

    non_organic_installs: typing.Optional[int] = pydantic.Field(
        None,
        description="Non-Organic Installs.",
    )

    organic_installs: typing.Optional[int] = pydantic.Field(
        None,
        description="Organic Installs.",
    )

    roas_ad: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="ROAS (Ad Revenue).",
    )

    roas: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="ROAS (All Revenue).",
    )

    roas_iap: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="ROAS (IAP Revenue).",
    )

    reattributions: typing.Optional[int] = pydantic.Field(
        None,
        description="Reattributions.",
    )

    return_on_investment: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Return On Investment (ROI).",
    )

    revenue: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Revenue.",
    )

    cohort_revenue: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Revenue (Cohort).",
    )

    revenue_events: typing.Optional[int] = pydantic.Field(
        None,
        description="Revenue Events.",
    )

    revenue_to_cost: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="Revenue To Cost Ratio (RCR).",
    )

    sessions: typing.Optional[int] = pydantic.Field(
        None,
        description="Sessions.",
    )

    events: typing.Optional[int] = pydantic.Field(
        None,
        description="Total Events.",
    )

    ecpi_all: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="eCPI (All Installs).",
    )

    ecpi: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="eCPI (Paid Installs).",
    )

    ecpm: typing.Optional[decimal.Decimal] = pydantic.Field(
        None,
        description="eCPM (Attribution).",
    )

    # Dimensions
    day: datetime.date = pydantic.Field(
        ...,
        description="Date.",
    )

    os_name: typing.Optional[str] = pydantic.Field(
        None,
        description="Operating system.",
    )

    device_type: typing.Optional[str] = pydantic.Field(
        None,
        description="Device, e.g., phone or tablet.",
    )

    app: typing.Optional[str] = pydantic.Field(
        None,
        description="Name of the app.",
    )

    app_token: typing.Optional[str] = pydantic.Field(
        None,
        description="App ID in the Adjust system.",
    )

    store_id: typing.Optional[str] = pydantic.Field(
        None,
        description="Store App ID.",
    )

    store_type: typing.Optional[str] = pydantic.Field(
        None,
        description="Store from where the app was installed.",
    )

    app_network: typing.Optional[str] = pydantic.Field(
        None,
        description="Value with format: <store_type>:<store_id>",
    )

    currency: typing.Optional[str] = pydantic.Field(
        None,
        description="Currency name.",
    )

    currency_code: typing.Optional[str] = pydantic.Field(
        None,
        description="3-character value ISO 4217.",
    )

    network: typing.Optional[str] = pydantic.Field(
        None,
        description="The name of the advertising network.",
    )

    campaign: typing.Optional[str] = pydantic.Field(
        None,
        description=("Tracker sub-level 1. String value usually " "contains campaign name and id."),
    )

    campaign_network: typing.Optional[str] = pydantic.Field(
        None,
        description="Campaign name from the network.",
    )

    campaign_id_network: typing.Optional[str] = pydantic.Field(
        None,
        description="Campaign ID from the network.",
    )

    adgroup: typing.Optional[str] = pydantic.Field(
        None,
        description=("Tracker sub-level 2. String value usually " "contains adgroup name and id."),
    )

    adgroup_network: typing.Optional[str] = pydantic.Field(
        None,
        description="Adgroup name from the network.",
    )

    adgroup_id_network: typing.Optional[str] = pydantic.Field(
        None,
        description="Adgroup ID from the network.",
    )

    source_network: typing.Optional[str] = pydantic.Field(
        None,
        description=("Optional value dependent on the network. " "Usually the same as adgroup_network."),
    )

    source_id_network: typing.Optional[str] = pydantic.Field(
        None,
        description="Value for source_app.",
    )

    creative: typing.Optional[str] = pydantic.Field(
        None,
        description=("Tracker sub-level 3. String value usually " "contains creative name and id."),
    )

    creative_network: typing.Optional[str] = pydantic.Field(
        None,
        description="Creative name from the network.",
    )

    creative_id_network: typing.Optional[str] = pydantic.Field(
        None,
        description="Creative ID from the network.",
    )

    country: typing.Optional[str] = pydantic.Field(
        None,
        description="Country name.",
    )

    country_code: typing.Optional[str] = pydantic.Field(
        None,
        description="2-character value ISO 3166.",
    )

    region: typing.Optional[str] = pydantic.Field(
        None,
        description="Business region.",
    )

    partner_name: typing.Optional[str] = pydantic.Field(
        None,
        description="Partner's name in the Adjust system.",
    )

    partner_id: typing.Optional[str] = pydantic.Field(
        None,
        description="Partner’s id in the Adjust system.",
    )

    class Config:
        @staticmethod
        def schema_extra(schema: typing.Dict[str, typing.Any]):
            schema["$schema"] = "http://json-schema.org/draft-07/schema#"
