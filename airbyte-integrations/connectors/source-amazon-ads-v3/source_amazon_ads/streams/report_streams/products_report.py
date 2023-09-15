#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from copy import copy

from .report_streams_v3 import RecordType, ReportStreamV3

METRICS_MAP = {
    "campaigns": ["campaignName", "campaignId", "campaignStatus", "campaignBudgetAmount", "campaignBudgetType", "campaignRuleBasedBudgetAmount", "campaignApplicableBudgetRuleId", "campaignApplicableBudgetRuleName", "campaignBudgetCurrencyCode", "topOfSearchImpressionShare", "impressions", "clicks", "cost", "purchases1d", "purchases7d", "purchases14d", "purchases30d", "purchasesSameSku1d", "purchasesSameSku7d", "purchasesSameSku14d", "purchasesSameSku30d", "unitsSoldClicks1d", "unitsSoldClicks7d", "unitsSoldClicks14d", "unitsSoldClicks30d", "sales1d", "sales7d", "sales14d", "sales30d", "attributedSalesSameSku1d", "attributedSalesSameSku7d", "attributedSalesSameSku14d", "attributedSalesSameSku30d", "unitsSoldSameSku1d", "unitsSoldSameSku7d", "unitsSoldSameSku14d", "unitsSoldSameSku30d", "kindleEditionNormalizedPagesRead14d", "kindleEditionNormalizedPagesRoyalties14d", "date", "campaignBiddingStrategy", "costPerClick", "clickThroughRate", "spend"],
    "campaigns_adGroups":["campaignName", "campaignId", "campaignStatus", "campaignBudgetAmount", "campaignBudgetType", "campaignRuleBasedBudgetAmount", "campaignApplicableBudgetRuleId", "campaignApplicableBudgetRuleName", "campaignBudgetCurrencyCode", "impressions", "clicks", "cost", "purchases1d", "purchases7d", "purchases14d", "purchases30d", "purchasesSameSku1d", "purchasesSameSku7d", "purchasesSameSku14d", "purchasesSameSku30d", "unitsSoldClicks1d", "unitsSoldClicks7d", "unitsSoldClicks14d", "unitsSoldClicks30d", "sales1d", "sales7d", "sales14d", "sales30d", "attributedSalesSameSku1d", "attributedSalesSameSku7d", "attributedSalesSameSku14d", "attributedSalesSameSku30d", "unitsSoldSameSku1d", "unitsSoldSameSku7d", "unitsSoldSameSku14d", "unitsSoldSameSku30d", "kindleEditionNormalizedPagesRead14d", "kindleEditionNormalizedPagesRoyalties14d", "date",  "campaignBiddingStrategy", "costPerClick", "clickThroughRate", "spend","adGroupName", "adGroupId", "adStatus"],#, "topOfSearchImpressionShare","startDate", "endDate",
    "campaigns_placement":["campaignName", "campaignId", "campaignStatus", "campaignBudgetAmount", "campaignBudgetType", "campaignRuleBasedBudgetAmount", "campaignApplicableBudgetRuleId", "campaignApplicableBudgetRuleName", "campaignBudgetCurrencyCode", "impressions", "clicks", "cost", "purchases1d", "purchases7d", "purchases14d", "purchases30d", "purchasesSameSku1d", "purchasesSameSku7d", "purchasesSameSku14d", "purchasesSameSku30d", "unitsSoldClicks1d", "unitsSoldClicks7d", "unitsSoldClicks14d", "unitsSoldClicks30d", "sales1d", "sales7d", "sales14d", "sales30d", "attributedSalesSameSku1d", "attributedSalesSameSku7d", "attributedSalesSameSku14d", "attributedSalesSameSku30d", "unitsSoldSameSku1d", "unitsSoldSameSku7d", "unitsSoldSameSku14d", "unitsSoldSameSku30d", "kindleEditionNormalizedPagesRead14d", "kindleEditionNormalizedPagesRoyalties14d", "date", "campaignBiddingStrategy", "costPerClick", "clickThroughRate", "spend","placementClassification"],#, "startDate", "endDate", "topOfSearchImpressionShare"
    "targeting":["adKeywordStatus","impressions", "clicks", "costPerClick", "clickThroughRate", "cost", "purchases1d", "purchases7d", "purchases14d", "purchases30d", "purchasesSameSku1d", "purchasesSameSku7d", "purchasesSameSku14d", "purchasesSameSku30d", "unitsSoldClicks1d", "unitsSoldClicks7d", "unitsSoldClicks14d", "unitsSoldClicks30d", "sales1d", "sales7d", "sales14d", "sales30d", "attributedSalesSameSku1d", "attributedSalesSameSku7d", "attributedSalesSameSku14d", "attributedSalesSameSku30d", "unitsSoldSameSku1d", "unitsSoldSameSku7d", "unitsSoldSameSku14d", "unitsSoldSameSku30d", "kindleEditionNormalizedPagesRead14d", "kindleEditionNormalizedPagesRoyalties14d", "salesOtherSku7d", "unitsSoldOtherSku7d", "acosClicks7d", "acosClicks14d", "roasClicks7d", "roasClicks14d", "keywordId", "keyword", "campaignBudgetCurrencyCode", "date", "portfolioId", "campaignName", "campaignId", "campaignBudgetType", "campaignBudgetAmount", "campaignStatus", "keywordBid", "adGroupName", "adGroupId", "keywordType", "matchType", "targeting", "topOfSearchImpressionShare"],#, "startDate", "endDate"
    "search_term":["impressions", "clicks", "costPerClick", "clickThroughRate", "cost", "purchases1d", "purchases7d", "purchases14d", "purchases30d", "purchasesSameSku1d", "purchasesSameSku7d", "purchasesSameSku14d", "purchasesSameSku30d", "unitsSoldClicks1d", "unitsSoldClicks7d", "unitsSoldClicks14d", "unitsSoldClicks30d", "sales1d", "sales7d", "sales14d", "sales30d", "attributedSalesSameSku1d", "attributedSalesSameSku7d", "attributedSalesSameSku14d", "attributedSalesSameSku30d", "unitsSoldSameSku1d", "unitsSoldSameSku7d", "unitsSoldSameSku14d", "unitsSoldSameSku30d", "kindleEditionNormalizedPagesRead14d", "kindleEditionNormalizedPagesRoyalties14d", "salesOtherSku7d", "unitsSoldOtherSku7d", "acosClicks7d", "acosClicks14d", "roasClicks7d", "roasClicks14d", "keywordId", "keyword", "campaignBudgetCurrencyCode", "date", "portfolioId", "searchTerm", "campaignName", "campaignId", "campaignBudgetType", "campaignBudgetAmount", "campaignStatus", "keywordBid", "adGroupName", "adGroupId", "keywordType", "matchType", "targeting","adKeywordStatus"],#, "startDate", "endDate"
    "advertised_product":["date", "campaignName", "campaignId", "adGroupName", "adGroupId", "adId", "portfolioId", "impressions", "clicks", "costPerClick", "clickThroughRate", "cost", "spend", "campaignBudgetCurrencyCode", "campaignBudgetAmount", "campaignBudgetType", "campaignStatus", "advertisedAsin", "advertisedSku", "purchases1d", "purchases7d", "purchases14d", "purchases30d", "purchasesSameSku1d", "purchasesSameSku7d", "purchasesSameSku14d", "purchasesSameSku30d", "unitsSoldClicks1d", "unitsSoldClicks7d", "unitsSoldClicks14d", "unitsSoldClicks30d", "sales1d", "sales7d", "sales14d", "sales30d", "attributedSalesSameSku1d", "attributedSalesSameSku7d", "attributedSalesSameSku14d", "attributedSalesSameSku30d", "salesOtherSku7d", "unitsSoldSameSku1d", "unitsSoldSameSku7d", "unitsSoldSameSku14d", "unitsSoldSameSku30d", "unitsSoldOtherSku7d", "kindleEditionNormalizedPagesRead14d", "kindleEditionNormalizedPagesRoyalties14d", "acosClicks7d", "acosClicks14d", "roasClicks7d", "roasClicks14d"],#, "startDate", "endDate"
    "purchased_product":["date", "portfolioId", "campaignName", "campaignId", "adGroupName", "adGroupId", "keywordId", "keyword", "keywordType", "advertisedAsin", "purchasedAsin", "advertisedSku", "campaignBudgetCurrencyCode", "matchType", "unitsSoldClicks1d", "unitsSoldClicks7d", "unitsSoldClicks14d", "unitsSoldClicks30d", "sales1d", "sales7d", "sales14d", "sales30d", "purchases1d", "purchases7d", "purchases14d", "purchases30d", "unitsSoldOtherSku1d", "unitsSoldOtherSku7d", "unitsSoldOtherSku14d", "unitsSoldOtherSku30d", "salesOtherSku1d", "salesOtherSku7d", "salesOtherSku14d", "salesOtherSku30d", "purchasesOtherSku1d", "purchasesOtherSku7d", "purchasesOtherSku14d", "purchasesOtherSku30d", "kindleEditionNormalizedPagesRead14d", "kindleEditionNormalizedPagesRoyalties14d"],#, "startDate", "endDate" 
}


METRICS_TYPE_TO_ID_MAP = {
    "campaigns": "campaignId",
    "campaigns_adGroups": "adGroupId",
    "campaigns_placement": "campaignId",
    "targeting": "targeting",
    "search_term": "keywordId",
    "advertised_product": "advertisedAsin",
    "purchased_product": "purchasedAsin",
}

class AirbytePurchasedProductSp(ReportStreamV3):
    """
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Reports
    """

    def report_init_endpoint(self) -> str:
        return f"/reporting/reports"

    metrics_map = {"purchased_product":METRICS_MAP["purchased_product"]}
    metrics_type_to_id_map = {
    "purchased_product": "purchasedAsin"
    }


    def _get_init_report_body(self, start_date, end_date, record_type: str, profile):
        metrics_list = self.metrics_map[record_type]
        self.logger.info(f"abhinandan 0,{record_type} ")
        if RecordType.PURCHASEDPRODUCT in record_type:
            return {
                "name":"SP purchased product report 7/5-7/10",
                "startDate": start_date,
                "endDate": end_date,
                "configuration":{
                    "adProduct":"SPONSORED_PRODUCTS",
                    "groupBy":["asin"],
                    "columns": metrics_list,
                    "reportTypeId":"spPurchasedProduct",
                    "timeUnit":"DAILY",
                    "format":"GZIP_JSON"
                }
            }




class AirbyteAdvertisedProductSp(ReportStreamV3):
    """
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Reports
    """

    def report_init_endpoint(self) -> str:
        return f"/reporting/reports"

    metrics_map = {"advertised_product":METRICS_MAP["advertised_product"]}
    metrics_type_to_id_map = {
    "advertised_product": "advertisedAsin"
    }


    def _get_init_report_body(self, start_date, end_date, record_type: str, profile):
        metrics_list = self.metrics_map[record_type]
        self.logger.info(f"abhinandan 0,{record_type} ")
        if RecordType.ADVERTISEDPRODUCT in record_type:
            return {
                "name":"SP advertised product report 7/5-7/10",
                "startDate": start_date,
                "endDate": end_date,
                "configuration":{
                    "adProduct":"SPONSORED_PRODUCTS",
                    "groupBy":["advertiser"],
                    "columns": metrics_list,
                    "reportTypeId":"spAdvertisedProduct",
                    "timeUnit":"DAILY",
                    "format":"GZIP_JSON"
                }
            }



class AirbyteSearchTermSp(ReportStreamV3):
    """
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Reports
    """

    def report_init_endpoint(self) -> str:
        return f"/reporting/reports"

    metrics_map = {"search_term":METRICS_MAP["search_term"]}
    metrics_type_to_id_map = {
    "search_term": "keywordId"
    }


    def _get_init_report_body(self, start_date, end_date, record_type: str, profile):
        metrics_list = self.metrics_map[record_type]
        self.logger.info(f"abhinandan 0,{record_type} ")
        if RecordType.SEARCHTERM in record_type:
            return {
                "name":"SP search term report 7/5-7/10",
                "startDate": start_date,
                "endDate": end_date,
                "configuration":{
                    "adProduct":"SPONSORED_PRODUCTS",
                    "groupBy":["searchTerm"],
                    "columns": metrics_list,
                    "reportTypeId":"spSearchTerm",
                    "timeUnit":"DAILY",
                    "format":"GZIP_JSON"
                }
            }


class AirbyteTargetingSp(ReportStreamV3):
    """
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Reports
    """

    def report_init_endpoint(self) -> str:
        return f"/reporting/reports"

    metrics_map = {"targeting":METRICS_MAP["targeting"]}
    metrics_type_to_id_map = {
    "targeting": "targeting"
    }


    def _get_init_report_body(self, start_date, end_date, record_type: str, profile):
        metrics_list = self.metrics_map[record_type]
        self.logger.info(f"abhinandan 0,{record_type} ")
        if RecordType.TARGETS in record_type:
            return {
                "name":"SP targeting report 7/5-7/10",
                "startDate": start_date,
                "endDate": end_date,
                "configuration":{
                    "adProduct":"SPONSORED_PRODUCTS",
                    "groupBy":["targeting"],
                    "columns": metrics_list,
                    "reportTypeId":"spTargeting",
                    "timeUnit":"DAILY",
                    "format":"GZIP_JSON"
                }
            }



class AirbyteCampPlacementSp(ReportStreamV3):
    """
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Reports
    """

    def report_init_endpoint(self) -> str:
        return f"/reporting/reports"

    metrics_map = {"campaigns_placement":METRICS_MAP["campaigns_placement"]}
    metrics_type_to_id_map = {
    "campaigns_placement": "campaignId"
    }


    def _get_init_report_body(self, start_date, end_date, record_type: str, profile):
        metrics_list = self.metrics_map[record_type]
        self.logger.info(f"abhinandan 0,{record_type} ")
        if RecordType.CAMPAIGNS in record_type:
            return {
                "name":"SP campaigns report 7/5-7/10",
                "startDate": start_date,
                "endDate": end_date,
                "configuration":{
                    "adProduct":"SPONSORED_PRODUCTS",
                    "groupBy":["campaign","campaignPlacement"],
                    "columns": metrics_list,
                    "reportTypeId":"spCampaigns",
                    "timeUnit":"DAILY",
                    "format":"GZIP_JSON"
                }
            }


class AirbyteCampAdgroupsSp(ReportStreamV3):
    """
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Reports
    """

    def report_init_endpoint(self) -> str:
        return f"/reporting/reports"

    metrics_map = {"campaigns_adGroups":METRICS_MAP["campaigns_adGroups"]}
    metrics_type_to_id_map = {
    "campaigns_adGroups": "adGroupId"
    }


    def _get_init_report_body(self, start_date, end_date, record_type: str, profile):
        metrics_list = self.metrics_map[record_type]
        self.logger.info(f"abhinandan 0,{record_type} ")
        if RecordType.CAMPAIGNS in record_type:
            return {
                "name":"SP campaigns report 7/5-7/10",
                "startDate": start_date,
                "endDate": end_date,
                "configuration":{
                    "adProduct":"SPONSORED_PRODUCTS",
                    "groupBy":["campaign","adGroup"],
                    "columns": metrics_list,
                    "reportTypeId":"spCampaigns",
                    "timeUnit":"DAILY",
                    "format":"GZIP_JSON"
                }
            }


class AirbyteCampSp(ReportStreamV3):
    """
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Reports
    """

    def report_init_endpoint(self) -> str:
        return f"/reporting/reports"

    metrics_map = {"campaigns":METRICS_MAP["campaigns"]}
    metrics_type_to_id_map = {
    "campaigns": "campaignId"
    }


    def _get_init_report_body(self, start_date, end_date, record_type: str, profile):
        metrics_list = self.metrics_map[record_type]
        self.logger.info(f"abhinandan 0,{record_type} ")
        if RecordType.CAMPAIGNS in record_type:
            return {
                "name":"SP campaigns report 7/5-7/10",
                "startDate": start_date,
                "endDate": end_date,
                "configuration":{
                    "adProduct":"SPONSORED_PRODUCTS",
                    "groupBy":["campaign"],
                    "columns": metrics_list,
                    "reportTypeId":"spCampaigns",
                    "timeUnit":"DAILY",
                    "format":"GZIP_JSON"
                }
            }



class AirbytePurchasedProductLastMonthSp(ReportStreamV3):
    """
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Reports
    """

    def report_init_endpoint(self) -> str:
        return f"/reporting/reports"

    metrics_map = {"purchased_product":METRICS_MAP["purchased_product"]}
    metrics_type_to_id_map = {
    "purchased_product": "purchasedAsin"
    }


    def _get_init_report_body(self, start_date, end_date, record_type: str, profile):
        metrics_list = self.metrics_map[record_type]
        self.logger.info(f"abhinandan 0,{record_type} ")
        if RecordType.PURCHASEDPRODUCT in record_type:
            return {
                "name":"SP purchased product report 7/5-7/10",
                "startDate": start_date,
                "endDate": end_date,
                "configuration":{
                    "adProduct":"SPONSORED_PRODUCTS",
                    "groupBy":["asin"],
                    "columns": metrics_list,
                    "reportTypeId":"spPurchasedProduct",
                    "timeUnit":"DAILY",
                    "format":"GZIP_JSON"
                }
            }




class AirbyteAdvertisedProductLastMonthSp(ReportStreamV3):
    """
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Reports
    """

    def report_init_endpoint(self) -> str:
        return f"/reporting/reports"

    metrics_map = {"advertised_product":METRICS_MAP["advertised_product"]}
    metrics_type_to_id_map = {
    "advertised_product": "advertisedAsin"
    }


    def _get_init_report_body(self, start_date, end_date, record_type: str, profile):
        metrics_list = self.metrics_map[record_type]
        self.logger.info(f"abhinandan 0,{record_type} ")
        if RecordType.ADVERTISEDPRODUCT in record_type:
            return {
                "name":"SP advertised product report 7/5-7/10",
                "startDate": start_date,
                "endDate": end_date,
                "configuration":{
                    "adProduct":"SPONSORED_PRODUCTS",
                    "groupBy":["advertiser"],
                    "columns": metrics_list,
                    "reportTypeId":"spAdvertisedProduct",
                    "timeUnit":"DAILY",
                    "format":"GZIP_JSON"
                }
            }



class AirbyteSearchTermLastMonthSp(ReportStreamV3):
    """
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Reports
    """

    def report_init_endpoint(self) -> str:
        return f"/reporting/reports"

    metrics_map = {"search_term":METRICS_MAP["search_term"]}
    metrics_type_to_id_map = {
    "search_term": "keywordId"
    }


    def _get_init_report_body(self, start_date, end_date, record_type: str, profile):
        metrics_list = self.metrics_map[record_type]
        self.logger.info(f"abhinandan 0,{record_type} ")
        if RecordType.SEARCHTERM in record_type:
            return {
                "name":"SP search term report 7/5-7/10",
                "startDate": start_date,
                "endDate": end_date,
                "configuration":{
                    "adProduct":"SPONSORED_PRODUCTS",
                    "groupBy":["searchTerm"],
                    "columns": metrics_list,
                    "reportTypeId":"spSearchTerm",
                    "timeUnit":"DAILY",
                    "format":"GZIP_JSON"
                }
            }


class AirbyteTargetingLastMonthSp(ReportStreamV3):
    """
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Reports
    """

    def report_init_endpoint(self) -> str:
        return f"/reporting/reports"

    metrics_map = {"targeting":METRICS_MAP["targeting"]}
    metrics_type_to_id_map = {
    "targeting": "targeting"
    }


    def _get_init_report_body(self, start_date, end_date, record_type: str, profile):
        metrics_list = self.metrics_map[record_type]
        self.logger.info(f"abhinandan 0,{record_type} ")
        if RecordType.TARGETS in record_type:
            return {
                "name":"SP targeting report 7/5-7/10",
                "startDate": start_date,
                "endDate": end_date,
                "configuration":{
                    "adProduct":"SPONSORED_PRODUCTS",
                    "groupBy":["targeting"],
                    "columns": metrics_list,
                    "reportTypeId":"spTargeting",
                    "timeUnit":"DAILY",
                    "format":"GZIP_JSON"
                }
            }



class AirbyteCampPlacementLastMonthSp(ReportStreamV3):
    """
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Reports
    """

    def report_init_endpoint(self) -> str:
        return f"/reporting/reports"

    metrics_map = {"campaigns_placement":METRICS_MAP["campaigns_placement"]}
    metrics_type_to_id_map = {
    "campaigns_placement": "campaignId"
    }


    def _get_init_report_body(self, start_date, end_date, record_type: str, profile):
        metrics_list = self.metrics_map[record_type]
        self.logger.info(f"abhinandan 0,{record_type} ")
        if RecordType.CAMPAIGNS in record_type:
            return {
                "name":"SP campaigns report 7/5-7/10",
                "startDate": start_date,
                "endDate": end_date,
                "configuration":{
                    "adProduct":"SPONSORED_PRODUCTS",
                    "groupBy":["campaign","campaignPlacement"],
                    "columns": metrics_list,
                    "reportTypeId":"spCampaigns",
                    "timeUnit":"DAILY",
                    "format":"GZIP_JSON"
                }
            }


class AirbyteCampAdgroupsLastMonthSp(ReportStreamV3):
    """
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Reports
    """

    def report_init_endpoint(self) -> str:
        return f"/reporting/reports"

    metrics_map = {"campaigns_adGroups":METRICS_MAP["campaigns_adGroups"]}
    metrics_type_to_id_map = {
    "campaigns_adGroups": "adGroupId"
    }


    def _get_init_report_body(self, start_date, end_date, record_type: str, profile):
        metrics_list = self.metrics_map[record_type]
        self.logger.info(f"abhinandan 0,{record_type} ")
        if RecordType.CAMPAIGNS in record_type:
            return {
                "name":"SP campaigns report 7/5-7/10",
                "startDate": start_date,
                "endDate": end_date,
                "configuration":{
                    "adProduct":"SPONSORED_PRODUCTS",
                    "groupBy":["campaign","adGroup"],
                    "columns": metrics_list,
                    "reportTypeId":"spCampaigns",
                    "timeUnit":"DAILY",
                    "format":"GZIP_JSON"
                }
            }


class AirbyteCampLastMonthSp(ReportStreamV3):
    """
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Reports
    """

    def report_init_endpoint(self) -> str:
        return f"/reporting/reports"

    metrics_map = {"campaigns":METRICS_MAP["campaigns"]}
    metrics_type_to_id_map = {
    "campaigns": "campaignId"
    }


    def _get_init_report_body(self, start_date, end_date, record_type: str, profile):
        metrics_list = self.metrics_map[record_type]
        self.logger.info(f"abhinandan 0,{record_type} ")
        if RecordType.CAMPAIGNS in record_type:
            return {
                "name":"SP campaigns report 7/5-7/10",
                "startDate": start_date,
                "endDate": end_date,
                "configuration":{
                    "adProduct":"SPONSORED_PRODUCTS",
                    "groupBy":["campaign"],
                    "columns": metrics_list,
                    "reportTypeId":"spCampaigns",
                    "timeUnit":"DAILY",
                    "format":"GZIP_JSON"
                }
            }



class SponsoredProductsReportStream(ReportStreamV3):
    """
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Reports
    """

    def report_init_endpoint(self) -> str:
        return f"/reporting/reports"

    metrics_map = {"campaigns":METRICS_MAP["campaigns"]}
    metrics_type_to_id_map = {
    "campaigns": "campaignId"
    }


    def _get_init_report_body(self, start_date, end_date, record_type: str, profile):
        metrics_list = self.metrics_map[record_type]
        self.logger.info(f"abhinandan 0,{record_type} ")
        if RecordType.CAMPAIGNS in record_type:
            return {
                "name":"SP campaigns report 7/5-7/10",
                "startDate": start_date,
                "endDate": end_date,
                "configuration":{
                    "adProduct":"SPONSORED_PRODUCTS",
                    "groupBy":["campaign"],
                    "columns": metrics_list,
                    "reportTypeId":"spCampaigns",
                    "timeUnit":"DAILY",
                    "format":"GZIP_JSON"
                }
            }






        