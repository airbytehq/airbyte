# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from test_hourly_reports import HourlyReportsTestWithStateChangesAfterMigration, get_state_after_migration
from test_report_stream import TestSuiteReportStream


class TestBaseProductDimensionPerformanceReport(TestSuiteReportStream):
    state_file_after_migration = "non_hourly_reports_state_after_migration"
    state_file_after_migration_with_cursor_further_config_start_date = (
        "non_hourly_reports_state_after_migration_with_cursor_further_config_start_date"
    )
    first_read_state = get_state_after_migration(time_period="2024-05-17", account_id=TestSuiteReportStream.account_id)
    second_read_state = get_state_after_migration(time_period="2023-12-25", account_id=TestSuiteReportStream.account_id)
    first_read_state_for_records_further_start_date = get_state_after_migration(
        time_period="2024-05-06", account_id=TestSuiteReportStream.account_id
    )
    second_read_state_for_records_further_start_date = get_state_after_migration(
        time_period="2024-05-07", account_id=TestSuiteReportStream.account_id
    )
    second_read_state_for_records_before_start_date = get_state_after_migration(
        time_period="2024-01-01", account_id=TestSuiteReportStream.account_id
    )

    def mock_report_apis(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )

        self.mock_generate_report_api(
            endpoint="Poll", response_template="generate_report_poll", body=b'{"ReportRequestId": "thisisthereport_requestid"}'
        )


class TestProductDimensionPerformanceReportDailyStream(TestBaseProductDimensionPerformanceReport):
    stream_name = "product_dimension_performance_report_daily"
    report_file = "product_dimension_performance_report_daily"
    incremental_report_file = "product_dimension_performance_report_daily_incremental"
    incremental_report_file_with_records_further_cursor = (
        "product_dimension_performance_report_daily_incremental_with_records_further_cursor"
    )
    report_file_with_records_further_start_date = "product_dimension_performance_report_daily_with_records_further_start_date"
    records_number = 8

    state_file = "product_dimension_performance_report_daily_state"
    state_file_legacy = "product_dimension_performance_report_daily_state"

    def mock_report_apis(self):
        super().mock_report_apis()
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "ProductDimensionPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "ProductDimensionPerformanceReportRequest", "Aggregation": "Daily", "Columns": ["TimePeriod", "AccountName", "AccountNumber", "AdGroupName", "AdGroupId", "CampaignStatus", "AccountStatus", "AdGroupStatus", "Network", "AdId", "CampaignId", "CampaignName", "CurrencyCode", "DeviceType", "Language", "MerchantProductId", "Title", "Condition", "Brand", "Price", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "Conversions", "ConversionRate", "Revenue", "RevenuePerConversion", "SellerName", "OfferLanguage", "CountryOfSale", "AdStatus", "AdDistribution", "ClickTypeId", "TotalClicksOnAdElements", "ClickType", "ReturnOnAdSpend", "BidStrategyType", "LocalStoreCode", "StoreId", "AssistedClicks", "AssistedConversions", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "CostPerConversion", "ViewThroughConversions", "Goal", "GoalType", "ProductBought", "QuantityBought", "AverageCpm", "ConversionsQualified", "AssistedConversionsQualified", "ViewThroughConversionsQualified", "ProductBoughtTitle", "GTIN", "MPN", "ViewThroughRevenue", "Sales", "CostPerSale", "RevenuePerSale", "Installs", "CostPerInstall", "RevenuePerInstall", "CampaignType", "AssetGroupId", "AssetGroupName", "AssetGroupStatus", "CustomLabel0", "CustomLabel1", "CustomLabel2", "CustomLabel3", "CustomLabel4", "ProductType1", "ProductType2", "ProductType3", "ProductType4", "ProductType5"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "ProductDimensionPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "ProductDimensionPerformanceReportRequest", "Aggregation": "Daily", "Columns": ["TimePeriod", "AccountName", "AccountNumber", "AdGroupName", "AdGroupId", "CampaignStatus", "AccountStatus", "AdGroupStatus", "Network", "AdId", "CampaignId", "CampaignName", "CurrencyCode", "DeviceType", "Language", "MerchantProductId", "Title", "Condition", "Brand", "Price", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "Conversions", "ConversionRate", "Revenue", "RevenuePerConversion", "SellerName", "OfferLanguage", "CountryOfSale", "AdStatus", "AdDistribution", "ClickTypeId", "TotalClicksOnAdElements", "ClickType", "ReturnOnAdSpend", "BidStrategyType", "LocalStoreCode", "StoreId", "AssistedClicks", "AssistedConversions", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "CostPerConversion", "ViewThroughConversions", "Goal", "GoalType", "ProductBought", "QuantityBought", "AverageCpm", "ConversionsQualified", "AssistedConversionsQualified", "ViewThroughConversionsQualified", "ProductBoughtTitle", "GTIN", "MPN", "ViewThroughRevenue", "Sales", "CostPerSale", "RevenuePerSale", "Installs", "CostPerInstall", "RevenuePerInstall", "CampaignType", "AssetGroupId", "AssetGroupName", "AssetGroupStatus", "CustomLabel0", "CustomLabel1", "CustomLabel2", "CustomLabel3", "CustomLabel4", "ProductType1", "ProductType2", "ProductType3", "ProductType4", "ProductType5"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 8, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "ProductDimensionPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "ProductDimensionPerformanceReportRequest", "Aggregation": "Daily", "Columns": ["TimePeriod", "AccountName", "AccountNumber", "AdGroupName", "AdGroupId", "CampaignStatus", "AccountStatus", "AdGroupStatus", "Network", "AdId", "CampaignId", "CampaignName", "CurrencyCode", "DeviceType", "Language", "MerchantProductId", "Title", "Condition", "Brand", "Price", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "Conversions", "ConversionRate", "Revenue", "RevenuePerConversion", "SellerName", "OfferLanguage", "CountryOfSale", "AdStatus", "AdDistribution", "ClickTypeId", "TotalClicksOnAdElements", "ClickType", "ReturnOnAdSpend", "BidStrategyType", "LocalStoreCode", "StoreId", "AssistedClicks", "AssistedConversions", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "CostPerConversion", "ViewThroughConversions", "Goal", "GoalType", "ProductBought", "QuantityBought", "AverageCpm", "ConversionsQualified", "AssistedConversionsQualified", "ViewThroughConversionsQualified", "ProductBoughtTitle", "GTIN", "MPN", "ViewThroughRevenue", "Sales", "CostPerSale", "RevenuePerSale", "Installs", "CostPerInstall", "RevenuePerInstall", "CampaignType", "AssetGroupId", "AssetGroupName", "AssetGroupStatus", "CustomLabel0", "CustomLabel1", "CustomLabel2", "CustomLabel3", "CustomLabel4", "ProductType1", "ProductType2", "ProductType3", "ProductType4", "ProductType5"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2023}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "ProductDimensionPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "ProductDimensionPerformanceReportRequest", "Aggregation": "Daily", "Columns": ["TimePeriod", "AccountName", "AccountNumber", "AdGroupName", "AdGroupId", "CampaignStatus", "AccountStatus", "AdGroupStatus", "Network", "AdId", "CampaignId", "CampaignName", "CurrencyCode", "DeviceType", "Language", "MerchantProductId", "Title", "Condition", "Brand", "Price", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "Conversions", "ConversionRate", "Revenue", "RevenuePerConversion", "SellerName", "OfferLanguage", "CountryOfSale", "AdStatus", "AdDistribution", "ClickTypeId", "TotalClicksOnAdElements", "ClickType", "ReturnOnAdSpend", "BidStrategyType", "LocalStoreCode", "StoreId", "AssistedClicks", "AssistedConversions", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "CostPerConversion", "ViewThroughConversions", "Goal", "GoalType", "ProductBought", "QuantityBought", "AverageCpm", "ConversionsQualified", "AssistedConversionsQualified", "ViewThroughConversionsQualified", "ProductBoughtTitle", "GTIN", "MPN", "ViewThroughRevenue", "Sales", "CostPerSale", "RevenuePerSale", "Installs", "CostPerInstall", "RevenuePerInstall", "CampaignType", "AssetGroupId", "AssetGroupName", "AssetGroupStatus", "CustomLabel0", "CustomLabel1", "CustomLabel2", "CustomLabel3", "CustomLabel4", "ProductType1", "ProductType2", "ProductType3", "ProductType4", "ProductType5"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 6, "Month": 5, "Year": 2024}, "CustomDateRangeEnd": {"Day": 8, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )


class TestProductDimensionPerformanceReportHourlyStream(HourlyReportsTestWithStateChangesAfterMigration):
    stream_name = "product_dimension_performance_report_hourly"
    report_file = "product_dimension_performance_report_hourly"
    records_number = 8
    state_file = "hourly_reports_state"
    incremental_report_file = "product_dimension_performance_report_hourly_incremental"

    report_file_with_records_further_start_date = "product_dimension_performance_report_hourly_with_record_further_config_start_date"
    state_file_legacy = "hourly_reports_state_legacy"
    state_file_after_migration = "hourly_reports_state_after_migration"
    state_file_after_migration_with_cursor_further_config_start_date = (
        "hourly_reports_state_after_migration_with_cursor_further_config_start_date"
    )
    incremental_report_file_with_records_further_cursor = (
        "product_dimension_performance_report_hourly_incremental_with_records_further_cursor"
    )

    def mock_report_apis(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "ProductDimensionPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "ProductDimensionPerformanceReportRequest", "Aggregation": "Hourly", "Columns": ["TimePeriod", "AccountName", "AccountNumber", "AdGroupName", "AdGroupId", "CampaignStatus", "AccountStatus", "AdGroupStatus", "Network", "AdId", "CampaignId", "CampaignName", "CurrencyCode", "DeviceType", "Language", "MerchantProductId", "Title", "Condition", "Brand", "Price", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "Conversions", "ConversionRate", "Revenue", "RevenuePerConversion", "SellerName", "OfferLanguage", "CountryOfSale", "AdStatus", "AdDistribution", "ClickTypeId", "TotalClicksOnAdElements", "ClickType", "ReturnOnAdSpend", "BidStrategyType", "LocalStoreCode", "StoreId", "AssistedClicks", "AssistedConversions", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "CostPerConversion", "ViewThroughConversions", "Goal", "GoalType", "ProductBought", "QuantityBought", "AverageCpm", "ConversionsQualified", "AssistedConversionsQualified", "ViewThroughConversionsQualified", "ProductBoughtTitle", "GTIN", "MPN", "ViewThroughRevenue", "Sales", "CostPerSale", "RevenuePerSale", "Installs", "CostPerInstall", "RevenuePerInstall", "CampaignType", "AssetGroupId", "AssetGroupName", "AssetGroupStatus", "CustomLabel0", "CustomLabel1", "CustomLabel2", "CustomLabel3", "CustomLabel4", "ProductType1", "ProductType2", "ProductType3", "ProductType4", "ProductType5"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        # # for second read
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "ProductDimensionPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "ProductDimensionPerformanceReportRequest", "Aggregation": "Hourly", "Columns": ["TimePeriod", "AccountName", "AccountNumber", "AdGroupName", "AdGroupId", "CampaignStatus", "AccountStatus", "AdGroupStatus", "Network", "AdId", "CampaignId", "CampaignName", "CurrencyCode", "DeviceType", "Language", "MerchantProductId", "Title", "Condition", "Brand", "Price", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "Conversions", "ConversionRate", "Revenue", "RevenuePerConversion", "SellerName", "OfferLanguage", "CountryOfSale", "AdStatus", "AdDistribution", "ClickTypeId", "TotalClicksOnAdElements", "ClickType", "ReturnOnAdSpend", "BidStrategyType", "LocalStoreCode", "StoreId", "AssistedClicks", "AssistedConversions", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "CostPerConversion", "ViewThroughConversions", "Goal", "GoalType", "ProductBought", "QuantityBought", "AverageCpm", "ConversionsQualified", "AssistedConversionsQualified", "ViewThroughConversionsQualified", "ProductBoughtTitle", "GTIN", "MPN", "ViewThroughRevenue", "Sales", "CostPerSale", "RevenuePerSale", "Installs", "CostPerInstall", "RevenuePerInstall", "CampaignType", "AssetGroupId", "AssetGroupName", "AssetGroupStatus", "CustomLabel0", "CustomLabel1", "CustomLabel2", "CustomLabel3", "CustomLabel4", "ProductType1", "ProductType2", "ProductType3", "ProductType4", "ProductType5"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 6, "Month": 5, "Year": 2024}, "CustomDateRangeEnd": {"Day": 8, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        # # for no config start date test
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "ProductDimensionPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "ProductDimensionPerformanceReportRequest", "Aggregation": "Hourly", "Columns": ["TimePeriod", "AccountName", "AccountNumber", "AdGroupName", "AdGroupId", "CampaignStatus", "AccountStatus", "AdGroupStatus", "Network", "AdId", "CampaignId", "CampaignName", "CurrencyCode", "DeviceType", "Language", "MerchantProductId", "Title", "Condition", "Brand", "Price", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "Conversions", "ConversionRate", "Revenue", "RevenuePerConversion", "SellerName", "OfferLanguage", "CountryOfSale", "AdStatus", "AdDistribution", "ClickTypeId", "TotalClicksOnAdElements", "ClickType", "ReturnOnAdSpend", "BidStrategyType", "LocalStoreCode", "StoreId", "AssistedClicks", "AssistedConversions", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "CostPerConversion", "ViewThroughConversions", "Goal", "GoalType", "ProductBought", "QuantityBought", "AverageCpm", "ConversionsQualified", "AssistedConversionsQualified", "ViewThroughConversionsQualified", "ProductBoughtTitle", "GTIN", "MPN", "ViewThroughRevenue", "Sales", "CostPerSale", "RevenuePerSale", "Installs", "CostPerInstall", "RevenuePerInstall", "CampaignType", "AssetGroupId", "AssetGroupName", "AssetGroupStatus", "CustomLabel0", "CustomLabel1", "CustomLabel2", "CustomLabel3", "CustomLabel4", "ProductType1", "ProductType2", "ProductType3", "ProductType4", "ProductType5"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2023}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        self.mock_generate_report_api(
            endpoint="Poll", response_template="generate_report_poll", body=b'{"ReportRequestId": "thisisthereport_requestid"}'
        )


class TestProductDimensionPerformanceReportWeeklyStream(TestBaseProductDimensionPerformanceReport):
    stream_name = "product_dimension_performance_report_weekly"
    report_file = "product_dimension_performance_report_weekly"
    incremental_report_file = "product_dimension_performance_report_weekly_incremental"
    incremental_report_file_with_records_further_cursor = (
        "product_dimension_performance_report_weekly_incremental_with_records_further_cursor"
    )
    report_file_with_records_further_start_date = "product_dimension_performance_report_weekly_with_records_further_start_date"
    records_number = 8

    state_file = "product_dimension_performance_report_weekly_state"
    state_file_legacy = "product_dimension_performance_report_weekly_state"

    def mock_report_apis(self):
        super().mock_report_apis()
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "ProductDimensionPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "ProductDimensionPerformanceReportRequest", "Aggregation": "Weekly", "Columns": ["TimePeriod", "AccountName", "AccountNumber", "AdGroupName", "AdGroupId", "CampaignStatus", "AccountStatus", "AdGroupStatus", "Network", "AdId", "CampaignId", "CampaignName", "CurrencyCode", "DeviceType", "Language", "MerchantProductId", "Title", "Condition", "Brand", "Price", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "Conversions", "ConversionRate", "Revenue", "RevenuePerConversion", "SellerName", "OfferLanguage", "CountryOfSale", "AdStatus", "AdDistribution", "ClickTypeId", "TotalClicksOnAdElements", "ClickType", "ReturnOnAdSpend", "BidStrategyType", "LocalStoreCode", "StoreId", "AssistedClicks", "AssistedConversions", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "CostPerConversion", "ViewThroughConversions", "Goal", "GoalType", "ProductBought", "QuantityBought", "AverageCpm", "ConversionsQualified", "AssistedConversionsQualified", "ViewThroughConversionsQualified", "ProductBoughtTitle", "GTIN", "MPN", "ViewThroughRevenue", "Sales", "CostPerSale", "RevenuePerSale", "Installs", "CostPerInstall", "RevenuePerInstall", "CampaignType", "AssetGroupId", "AssetGroupName", "AssetGroupStatus", "CustomLabel0", "CustomLabel1", "CustomLabel2", "CustomLabel3", "CustomLabel4", "ProductType1", "ProductType2", "ProductType3", "ProductType4", "ProductType5"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "ProductDimensionPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "ProductDimensionPerformanceReportRequest", "Aggregation": "Weekly", "Columns": ["TimePeriod", "AccountName", "AccountNumber", "AdGroupName", "AdGroupId", "CampaignStatus", "AccountStatus", "AdGroupStatus", "Network", "AdId", "CampaignId", "CampaignName", "CurrencyCode", "DeviceType", "Language", "MerchantProductId", "Title", "Condition", "Brand", "Price", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "Conversions", "ConversionRate", "Revenue", "RevenuePerConversion", "SellerName", "OfferLanguage", "CountryOfSale", "AdStatus", "AdDistribution", "ClickTypeId", "TotalClicksOnAdElements", "ClickType", "ReturnOnAdSpend", "BidStrategyType", "LocalStoreCode", "StoreId", "AssistedClicks", "AssistedConversions", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "CostPerConversion", "ViewThroughConversions", "Goal", "GoalType", "ProductBought", "QuantityBought", "AverageCpm", "ConversionsQualified", "AssistedConversionsQualified", "ViewThroughConversionsQualified", "ProductBoughtTitle", "GTIN", "MPN", "ViewThroughRevenue", "Sales", "CostPerSale", "RevenuePerSale", "Installs", "CostPerInstall", "RevenuePerInstall", "CampaignType", "AssetGroupId", "AssetGroupName", "AssetGroupStatus", "CustomLabel0", "CustomLabel1", "CustomLabel2", "CustomLabel3", "CustomLabel4", "ProductType1", "ProductType2", "ProductType3", "ProductType4", "ProductType5"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 8, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "ProductDimensionPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "ProductDimensionPerformanceReportRequest", "Aggregation": "Weekly", "Columns": ["TimePeriod", "AccountName", "AccountNumber", "AdGroupName", "AdGroupId", "CampaignStatus", "AccountStatus", "AdGroupStatus", "Network", "AdId", "CampaignId", "CampaignName", "CurrencyCode", "DeviceType", "Language", "MerchantProductId", "Title", "Condition", "Brand", "Price", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "Conversions", "ConversionRate", "Revenue", "RevenuePerConversion", "SellerName", "OfferLanguage", "CountryOfSale", "AdStatus", "AdDistribution", "ClickTypeId", "TotalClicksOnAdElements", "ClickType", "ReturnOnAdSpend", "BidStrategyType", "LocalStoreCode", "StoreId", "AssistedClicks", "AssistedConversions", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "CostPerConversion", "ViewThroughConversions", "Goal", "GoalType", "ProductBought", "QuantityBought", "AverageCpm", "ConversionsQualified", "AssistedConversionsQualified", "ViewThroughConversionsQualified", "ProductBoughtTitle", "GTIN", "MPN", "ViewThroughRevenue", "Sales", "CostPerSale", "RevenuePerSale", "Installs", "CostPerInstall", "RevenuePerInstall", "CampaignType", "AssetGroupId", "AssetGroupName", "AssetGroupStatus", "CustomLabel0", "CustomLabel1", "CustomLabel2", "CustomLabel3", "CustomLabel4", "ProductType1", "ProductType2", "ProductType3", "ProductType4", "ProductType5"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2023}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "ProductDimensionPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "ProductDimensionPerformanceReportRequest", "Aggregation": "Weekly", "Columns": ["TimePeriod", "AccountName", "AccountNumber", "AdGroupName", "AdGroupId", "CampaignStatus", "AccountStatus", "AdGroupStatus", "Network", "AdId", "CampaignId", "CampaignName", "CurrencyCode", "DeviceType", "Language", "MerchantProductId", "Title", "Condition", "Brand", "Price", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "Conversions", "ConversionRate", "Revenue", "RevenuePerConversion", "SellerName", "OfferLanguage", "CountryOfSale", "AdStatus", "AdDistribution", "ClickTypeId", "TotalClicksOnAdElements", "ClickType", "ReturnOnAdSpend", "BidStrategyType", "LocalStoreCode", "StoreId", "AssistedClicks", "AssistedConversions", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "CostPerConversion", "ViewThroughConversions", "Goal", "GoalType", "ProductBought", "QuantityBought", "AverageCpm", "ConversionsQualified", "AssistedConversionsQualified", "ViewThroughConversionsQualified", "ProductBoughtTitle", "GTIN", "MPN", "ViewThroughRevenue", "Sales", "CostPerSale", "RevenuePerSale", "Installs", "CostPerInstall", "RevenuePerInstall", "CampaignType", "AssetGroupId", "AssetGroupName", "AssetGroupStatus", "CustomLabel0", "CustomLabel1", "CustomLabel2", "CustomLabel3", "CustomLabel4", "ProductType1", "ProductType2", "ProductType3", "ProductType4", "ProductType5"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 6, "Month": 5, "Year": 2024}, "CustomDateRangeEnd": {"Day": 8, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )


class TestProductDimensionPerformanceReportMonthlyStream(TestBaseProductDimensionPerformanceReport):
    stream_name = "product_dimension_performance_report_monthly"
    report_file = "product_dimension_performance_report_monthly"
    incremental_report_file = "product_dimension_performance_report_monthly_incremental"
    incremental_report_file_with_records_further_cursor = (
        "product_dimension_performance_report_monthly_incremental_with_records_further_cursor"
    )
    report_file_with_records_further_start_date = "product_dimension_performance_report_monthly_with_records_further_start_date"
    records_number = 8

    state_file = "product_dimension_performance_report_monthly_state"
    state_file_legacy = "product_dimension_performance_report_monthly_state"

    def mock_report_apis(self):
        super().mock_report_apis()
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "ProductDimensionPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "ProductDimensionPerformanceReportRequest", "Aggregation": "Monthly", "Columns": ["TimePeriod", "AccountName", "AccountNumber", "AdGroupName", "AdGroupId", "CampaignStatus", "AccountStatus", "AdGroupStatus", "Network", "AdId", "CampaignId", "CampaignName", "CurrencyCode", "DeviceType", "Language", "MerchantProductId", "Title", "Condition", "Brand", "Price", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "Conversions", "ConversionRate", "Revenue", "RevenuePerConversion", "SellerName", "OfferLanguage", "CountryOfSale", "AdStatus", "AdDistribution", "ClickTypeId", "TotalClicksOnAdElements", "ClickType", "ReturnOnAdSpend", "BidStrategyType", "LocalStoreCode", "StoreId", "AssistedClicks", "AssistedConversions", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "CostPerConversion", "ViewThroughConversions", "Goal", "GoalType", "ProductBought", "QuantityBought", "AverageCpm", "ConversionsQualified", "AssistedConversionsQualified", "ViewThroughConversionsQualified", "ProductBoughtTitle", "GTIN", "MPN", "ViewThroughRevenue", "Sales", "CostPerSale", "RevenuePerSale", "Installs", "CostPerInstall", "RevenuePerInstall", "CampaignType", "AssetGroupId", "AssetGroupName", "AssetGroupStatus", "CustomLabel0", "CustomLabel1", "CustomLabel2", "CustomLabel3", "CustomLabel4", "ProductType1", "ProductType2", "ProductType3", "ProductType4", "ProductType5"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "ProductDimensionPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "ProductDimensionPerformanceReportRequest", "Aggregation": "Monthly", "Columns": ["TimePeriod", "AccountName", "AccountNumber", "AdGroupName", "AdGroupId", "CampaignStatus", "AccountStatus", "AdGroupStatus", "Network", "AdId", "CampaignId", "CampaignName", "CurrencyCode", "DeviceType", "Language", "MerchantProductId", "Title", "Condition", "Brand", "Price", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "Conversions", "ConversionRate", "Revenue", "RevenuePerConversion", "SellerName", "OfferLanguage", "CountryOfSale", "AdStatus", "AdDistribution", "ClickTypeId", "TotalClicksOnAdElements", "ClickType", "ReturnOnAdSpend", "BidStrategyType", "LocalStoreCode", "StoreId", "AssistedClicks", "AssistedConversions", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "CostPerConversion", "ViewThroughConversions", "Goal", "GoalType", "ProductBought", "QuantityBought", "AverageCpm", "ConversionsQualified", "AssistedConversionsQualified", "ViewThroughConversionsQualified", "ProductBoughtTitle", "GTIN", "MPN", "ViewThroughRevenue", "Sales", "CostPerSale", "RevenuePerSale", "Installs", "CostPerInstall", "RevenuePerInstall", "CampaignType", "AssetGroupId", "AssetGroupName", "AssetGroupStatus", "CustomLabel0", "CustomLabel1", "CustomLabel2", "CustomLabel3", "CustomLabel4", "ProductType1", "ProductType2", "ProductType3", "ProductType4", "ProductType5"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 8, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "ProductDimensionPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "ProductDimensionPerformanceReportRequest", "Aggregation": "Monthly", "Columns": ["TimePeriod", "AccountName", "AccountNumber", "AdGroupName", "AdGroupId", "CampaignStatus", "AccountStatus", "AdGroupStatus", "Network", "AdId", "CampaignId", "CampaignName", "CurrencyCode", "DeviceType", "Language", "MerchantProductId", "Title", "Condition", "Brand", "Price", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "Conversions", "ConversionRate", "Revenue", "RevenuePerConversion", "SellerName", "OfferLanguage", "CountryOfSale", "AdStatus", "AdDistribution", "ClickTypeId", "TotalClicksOnAdElements", "ClickType", "ReturnOnAdSpend", "BidStrategyType", "LocalStoreCode", "StoreId", "AssistedClicks", "AssistedConversions", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "CostPerConversion", "ViewThroughConversions", "Goal", "GoalType", "ProductBought", "QuantityBought", "AverageCpm", "ConversionsQualified", "AssistedConversionsQualified", "ViewThroughConversionsQualified", "ProductBoughtTitle", "GTIN", "MPN", "ViewThroughRevenue", "Sales", "CostPerSale", "RevenuePerSale", "Installs", "CostPerInstall", "RevenuePerInstall", "CampaignType", "AssetGroupId", "AssetGroupName", "AssetGroupStatus", "CustomLabel0", "CustomLabel1", "CustomLabel2", "CustomLabel3", "CustomLabel4", "ProductType1", "ProductType2", "ProductType3", "ProductType4", "ProductType5"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2023}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "ProductDimensionPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "ProductDimensionPerformanceReportRequest", "Aggregation": "Monthly", "Columns": ["TimePeriod", "AccountName", "AccountNumber", "AdGroupName", "AdGroupId", "CampaignStatus", "AccountStatus", "AdGroupStatus", "Network", "AdId", "CampaignId", "CampaignName", "CurrencyCode", "DeviceType", "Language", "MerchantProductId", "Title", "Condition", "Brand", "Price", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "Conversions", "ConversionRate", "Revenue", "RevenuePerConversion", "SellerName", "OfferLanguage", "CountryOfSale", "AdStatus", "AdDistribution", "ClickTypeId", "TotalClicksOnAdElements", "ClickType", "ReturnOnAdSpend", "BidStrategyType", "LocalStoreCode", "StoreId", "AssistedClicks", "AssistedConversions", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "CostPerConversion", "ViewThroughConversions", "Goal", "GoalType", "ProductBought", "QuantityBought", "AverageCpm", "ConversionsQualified", "AssistedConversionsQualified", "ViewThroughConversionsQualified", "ProductBoughtTitle", "GTIN", "MPN", "ViewThroughRevenue", "Sales", "CostPerSale", "RevenuePerSale", "Installs", "CostPerInstall", "RevenuePerInstall", "CampaignType", "AssetGroupId", "AssetGroupName", "AssetGroupStatus", "CustomLabel0", "CustomLabel1", "CustomLabel2", "CustomLabel3", "CustomLabel4", "ProductType1", "ProductType2", "ProductType3", "ProductType4", "ProductType5"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 6, "Month": 5, "Year": 2024}, "CustomDateRangeEnd": {"Day": 8, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
