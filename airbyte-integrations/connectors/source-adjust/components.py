#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.schema.json_file_schema_loader import JsonFileSchemaLoader

BASE_SCHEMA = {
    "properties": {
        "network_cost": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Ad Spend (Network).",
            "title": "Network Cost",
        },
        "network_cost_diff": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Ad Spend Diff (Network).",
            "title": "Network Cost Diff",
        },
        "network_clicks": {
            "anyOf": [{"type": "integer"}, {"type": "null"}],
            "default": None,
            "description": "Clicks (Network).",
            "title": "Network Clicks",
        },
        "network_impressions": {
            "anyOf": [{"type": "integer"}, {"type": "null"}],
            "default": None,
            "description": "Impressions (Network).",
            "title": "Network Impressions",
        },
        "network_installs": {
            "anyOf": [{"type": "integer"}, {"type": "null"}],
            "default": None,
            "description": "Installs (Network).",
            "title": "Network Installs",
        },
        "network_installs_diff": {
            "anyOf": [{"type": "integer"}, {"type": "null"}],
            "default": None,
            "description": "Installs Diff (Network).",
            "title": "Network Installs Diff",
        },
        "network_ecpc": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "eCPC (Network).",
            "title": "Network Ecpc",
        },
        "network_ecpi": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "eCPI (Network).",
            "title": "Network Ecpi",
        },
        "network_ecpm": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "eCPM (Network).",
            "title": "Network Ecpm",
        },
        "arpdau_ad": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "ARPDAU (Ad).",
            "title": "Arpdau Ad",
        },
        "arpdau": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "ARPDAU (All).",
            "title": "Arpdau",
        },
        "arpdau_iap": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "ARPDAU (IAP).",
            "title": "Arpdau Iap",
        },
        "ad_impressions": {
            "anyOf": [{"type": "integer"}, {"type": "null"}],
            "default": None,
            "description": "Ad Impressions.",
            "title": "Ad Impressions",
        },
        "ad_rpm": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Ad RPM.",
            "title": "Ad Rpm",
        },
        "ad_revenue": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Ad Revenue.",
            "title": "Ad Revenue",
        },
        "cohort_ad_revenue": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Ad Revenue (Cohort).",
            "title": "Cohort Ad Revenue",
        },
        "cost": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Ad Spend.",
            "title": "Cost",
        },
        "adjust_cost": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Ad Spend (Attribution).",
            "title": "Adjust Cost",
        },
        "all_revenue": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "All Revenue.",
            "title": "All Revenue",
        },
        "cohort_all_revenue": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "All Revenue (Cohort).",
            "title": "Cohort All Revenue",
        },
        "daus": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Avg. DAUs.",
            "title": "Daus",
        },
        "maus": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Avg. MAUs.",
            "title": "Maus",
        },
        "waus": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Avg. WAUs.",
            "title": "Waus",
        },
        "base_sessions": {
            "anyOf": [{"type": "integer"}, {"type": "null"}],
            "default": None,
            "description": "Base Sessions.",
            "title": "Base Sessions",
        },
        "ctr": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "CTR.",
            "title": "Ctr",
        },
        "click_conversion_rate": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Click Conversion Rate (CCR).",
            "title": "Click Conversion Rate",
        },
        "click_cost": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Click Cost.",
            "title": "Click Cost",
        },
        "clicks": {"anyOf": [{"type": "integer"}, {"type": "null"}], "default": None, "description": "Clicks.", "title": "Clicks"},
        "paid_clicks": {
            "anyOf": [{"type": "integer"}, {"type": "null"}],
            "default": None,
            "description": "Clicks (paid).",
            "title": "Paid Clicks",
        },
        "deattributions": {
            "anyOf": [{"type": "integer"}, {"type": "null"}],
            "default": None,
            "description": "Deattributions.",
            "title": "Deattributions",
        },
        "ecpc": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Effective Cost per Click (eCPC).",
            "title": "Ecpc",
        },
        "gdpr_forgets": {
            "anyOf": [{"type": "integer"}, {"type": "null"}],
            "default": None,
            "description": "GDPR Forgets.",
            "title": "Gdpr Forgets",
        },
        "gross_profit": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Gross profit.",
            "title": "Gross Profit",
        },
        "cohort_gross_profit": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Gross profit (Cohort).",
            "title": "Cohort Gross Profit",
        },
        "impression_conversion_rate": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Impression Conversion Rate (ICR).",
            "title": "Impression Conversion Rate",
        },
        "impression_cost": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Impression Cost.",
            "title": "Impression Cost",
        },
        "impressions": {
            "anyOf": [{"type": "integer"}, {"type": "null"}],
            "default": None,
            "description": "Impressions.",
            "title": "Impressions",
        },
        "paid_impressions": {
            "anyOf": [{"type": "integer"}, {"type": "null"}],
            "default": None,
            "description": "Impressions (paid).",
            "title": "Paid Impressions",
        },
        "install_cost": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Install Cost.",
            "title": "Install Cost",
        },
        "installs": {"anyOf": [{"type": "integer"}, {"type": "null"}], "default": None, "description": "Installs.", "title": "Installs"},
        "paid_installs": {
            "anyOf": [{"type": "integer"}, {"type": "null"}],
            "default": None,
            "description": "Installs (paid).",
            "title": "Paid Installs",
        },
        "installs_per_mile": {
            "anyOf": [{"type": "integer"}, {"type": "null"}],
            "default": None,
            "description": "Installs per Mille (IPM).",
            "title": "Installs Per Mile",
        },
        "limit_ad_tracking_installs": {
            "anyOf": [{"type": "integer"}, {"type": "null"}],
            "default": None,
            "description": "Limit Ad Tracking Installs.",
            "title": "Limit Ad Tracking Installs",
        },
        "limit_ad_tracking_install_rate": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Limit Ad Tracking Rate.",
            "title": "Limit Ad Tracking Install Rate",
        },
        "limit_ad_tracking_reattribution_rate": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Limit Ad Tracking Reattribution Rate.",
            "title": "Limit Ad Tracking Reattribution Rate",
        },
        "limit_ad_tracking_reattributions": {
            "anyOf": [{"type": "integer"}, {"type": "null"}],
            "default": None,
            "description": "Limit Ad Tracking Reattributions.",
            "title": "Limit Ad Tracking Reattributions",
        },
        "non_organic_installs": {
            "anyOf": [{"type": "integer"}, {"type": "null"}],
            "default": None,
            "description": "Non-Organic Installs.",
            "title": "Non Organic Installs",
        },
        "organic_installs": {
            "anyOf": [{"type": "integer"}, {"type": "null"}],
            "default": None,
            "description": "Organic Installs.",
            "title": "Organic Installs",
        },
        "roas_ad": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "ROAS (Ad Revenue).",
            "title": "Roas Ad",
        },
        "roas": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "ROAS (All Revenue).",
            "title": "Roas",
        },
        "roas_iap": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "ROAS (IAP Revenue).",
            "title": "Roas Iap",
        },
        "reattributions": {
            "anyOf": [{"type": "integer"}, {"type": "null"}],
            "default": None,
            "description": "Reattributions.",
            "title": "Reattributions",
        },
        "return_on_investment": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Return On Investment (ROI).",
            "title": "Return On Investment",
        },
        "revenue": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Revenue.",
            "title": "Revenue",
        },
        "cohort_revenue": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Revenue (Cohort).",
            "title": "Cohort Revenue",
        },
        "revenue_events": {
            "anyOf": [{"type": "integer"}, {"type": "null"}],
            "default": None,
            "description": "Revenue Events.",
            "title": "Revenue Events",
        },
        "revenue_to_cost": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Revenue To Cost Ratio (RCR).",
            "title": "Revenue To Cost",
        },
        "sessions": {"anyOf": [{"type": "integer"}, {"type": "null"}], "default": None, "description": "Sessions.", "title": "Sessions"},
        "events": {"anyOf": [{"type": "integer"}, {"type": "null"}], "default": None, "description": "Total Events.", "title": "Events"},
        "ecpi_all": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "eCPI (All Installs).",
            "title": "Ecpi All",
        },
        "ecpi": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "eCPI (Paid Installs).",
            "title": "Ecpi",
        },
        "ecpm": {
            "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "eCPM (Attribution).",
            "title": "Ecpm",
        },
        "day": {"description": "Date.", "format": "date", "title": "Day", "type": "string"},
        "os_name": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Operating system.",
            "title": "Os Name",
        },
        "device_type": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Device, e.g., phone or tablet.",
            "title": "Device Type",
        },
        "app": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None, "description": "Name of the app.", "title": "App"},
        "app_token": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "App ID in the Adjust system.",
            "title": "App Token",
        },
        "store_id": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None, "description": "Store App ID.", "title": "Store Id"},
        "store_type": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Store from where the app was installed.",
            "title": "Store Type",
        },
        "app_network": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Value with format: <store_type>:<store_id>",
            "title": "App Network",
        },
        "currency": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Currency name.",
            "title": "Currency",
        },
        "currency_code": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "3-character value ISO 4217.",
            "title": "Currency Code",
        },
        "network": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "The name of the advertising network.",
            "title": "Network",
        },
        "campaign": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Tracker sub-level 1. String value usually contains campaign name and id.",
            "title": "Campaign",
        },
        "campaign_network": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Campaign name from the network.",
            "title": "Campaign Network",
        },
        "campaign_id_network": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Campaign ID from the network.",
            "title": "Campaign Id Network",
        },
        "adgroup": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Tracker sub-level 2. String value usually contains adgroup name and id.",
            "title": "Adgroup",
        },
        "adgroup_network": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Adgroup name from the network.",
            "title": "Adgroup Network",
        },
        "adgroup_id_network": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Adgroup ID from the network.",
            "title": "Adgroup Id Network",
        },
        "source_network": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Optional value dependent on the network. Usually the same as adgroup_network.",
            "title": "Source Network",
        },
        "source_id_network": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Value for source_app.",
            "title": "Source Id Network",
        },
        "creative": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Tracker sub-level 3. String value usually contains creative name and id.",
            "title": "Creative",
        },
        "creative_network": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Creative name from the network.",
            "title": "Creative Network",
        },
        "creative_id_network": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Creative ID from the network.",
            "title": "Creative Id Network",
        },
        "country": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None, "description": "Country name.", "title": "Country"},
        "country_code": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "2-character value ISO 3166.",
            "title": "Country Code",
        },
        "region": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None, "description": "Business region.", "title": "Region"},
        "partner_name": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Partner's name in the Adjust system.",
            "title": "Partner Name",
        },
        "partner_id": {
            "anyOf": [{"type": "string"}, {"type": "null"}],
            "default": None,
            "description": "Partner’s id in the Adjust system.",
            "title": "Partner Id",
        },
    },
    "required": ["day"],
    "title": "Report",
    "type": "object",
}


@dataclass
class AdjustSchemaLoader(JsonFileSchemaLoader):

    config: Mapping[str, Any]

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Prune the schema to only include selected fields to synchronize.
        """
        schema = BASE_SCHEMA
        properties = schema["properties"]

        required = schema["required"]
        selected = self.config["metrics"] + self.config["dimensions"]
        retain = required + selected
        for attr in list(properties.keys()):
            if attr not in retain:
                del properties[attr]

        for attr in self.config["additional_metrics"]:
            properties[attr] = {"type": "number"}

        return schema
