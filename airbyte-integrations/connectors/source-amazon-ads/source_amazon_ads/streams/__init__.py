#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from .attribution_report import (
    AttributionReportPerformanceAdgroup,
    AttributionReportPerformanceCampaign,
    AttributionReportPerformanceCreative,
    AttributionReportProducts,
)
from .portfolios import Portfolios
from .profiles import Profiles
from .report_streams import (
    SponsoredBrandsReportStream,
    SponsoredBrandsV3ReportStream,
    SponsoredBrandsVideoReportStream,
    SponsoredDisplayReportStream,
    SponsoredProductsReportStream,
)
from .sponsored_brands import (
    SponsoredBrandsAdGroups,
    SponsoredBrandsCampaigns,
    SponsoredBrandsCampaignsV4,
    SponsoredBrandsKeywords
)
from .sponsored_display import (
    SponsoredDisplayAdGroups,
    SponsoredDisplayBudgetRules,
    SponsoredDisplayCampaigns,
    SponsoredDisplayCreatives,
    SponsoredDisplayProductAds,
    SponsoredDisplayTargetings,
)
from .sponsored_products import (
    SponsoredProductAdGroupBidRecommendations,
    SponsoredProductAdGroups,
    SponsoredProductAdGroupSuggestedKeywords,
    SponsoredProductAds,
    SponsoredProductCampaignNegativeKeywords,
    SponsoredProductCampaigns,
    SponsoredProductCampaignsV3,
    SponsoredProductKeywords,
    SponsoredProductNegativeKeywords,
    SponsoredProductTargetings,
)

__all__ = [
    "Portfolios",
    "Profiles",
    "SponsoredDisplayAdGroups",
    "SponsoredDisplayCampaigns",
    "SponsoredDisplayProductAds",
    "SponsoredDisplayTargetings",
    "SponsoredDisplayBudgetRules",
    "SponsoredProductAdGroups",
    "SponsoredDisplayCreatives",
    "SponsoredProductAdGroupBidRecommendations",
    "SponsoredProductAdGroupSuggestedKeywords",
    "SponsoredProductAds",
    "SponsoredProductCampaigns",
    "SponsoredProductCampaignsV3",
    "SponsoredProductKeywords",
    "SponsoredProductNegativeKeywords",
    "SponsoredProductCampaignNegativeKeywords",
    "SponsoredProductTargetings",
    "SponsoredBrandsCampaigns",
    "SponsoredBrandsCampaignsV4",
    "SponsoredBrandsAdGroups",
    "SponsoredBrandsKeywords",
    "SponsoredDisplayReportStream",
    "SponsoredProductsReportStream",
    "SponsoredBrandsReportStream",
    "SponsoredBrandsV3ReportStream",
    "SponsoredBrandsVideoReportStream",
    "AttributionReportPerformanceAdgroup",
    "AttributionReportPerformanceCampaign",
    "AttributionReportPerformanceCreative",
    "AttributionReportProducts",
]
