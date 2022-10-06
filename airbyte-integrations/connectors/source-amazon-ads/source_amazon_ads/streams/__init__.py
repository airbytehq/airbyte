#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from .attribution_report import (
    AttributionReportPerformanceAdgroup,
    AttributionReportPerformanceCampaign,
    AttributionReportPerformanceCreative,
    AttributionReportProducts,
)
from .profiles import Profiles
from .report_streams import (
    SponsoredBrandsReportStream,
    SponsoredBrandsVideoReportStream,
    SponsoredDisplayReportStream,
    SponsoredProductsReportStream,
)
from .sponsored_brands import SponsoredBrandsAdGroups, SponsoredBrandsCampaigns, SponsoredBrandsKeywords
from .sponsored_display import SponsoredDisplayAdGroups, SponsoredDisplayCampaigns, SponsoredDisplayProductAds, SponsoredDisplayTargetings
from .sponsored_products import (
    SponsoredProductAdGroups,
    SponsoredProductAds,
    SponsoredProductCampaigns,
    SponsoredProductKeywords,
    SponsoredProductNegativeKeywords,
    SponsoredProductTargetings,
)

__all__ = [
    "Profiles",
    "SponsoredDisplayAdGroups",
    "SponsoredDisplayCampaigns",
    "SponsoredDisplayProductAds",
    "SponsoredDisplayTargetings",
    "SponsoredProductAdGroups",
    "SponsoredProductAds",
    "SponsoredProductCampaigns",
    "SponsoredProductKeywords",
    "SponsoredProductNegativeKeywords",
    "SponsoredProductTargetings",
    "SponsoredBrandsCampaigns",
    "SponsoredBrandsAdGroups",
    "SponsoredBrandsKeywords",
    "SponsoredDisplayReportStream",
    "SponsoredProductsReportStream",
    "SponsoredBrandsReportStream",
    "SponsoredBrandsVideoReportStream",
    "AttributionReportPerformanceAdgroup",
    "AttributionReportPerformanceCampaign",
    "AttributionReportPerformanceCreative",
    "AttributionReportProducts",
]
