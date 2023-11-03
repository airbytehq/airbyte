#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import os
import ssl
import time
from abc import ABC, abstractmethod
from datetime import timezone
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from urllib.error import URLError

import pandas as pd
import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from bingads.service_client import ServiceClient
from bingads.v13.internal.reporting.row_report_iterator import _RowReportRecord
from bingads.v13.reporting.reporting_service_manager import ReportingServiceManager
from numpy import nan
from source_bing_ads.client import Client
from source_bing_ads.reports import (
    ALL_CONVERSION_FIELDS,
    ALL_REVENUE_FIELDS,
    AVERAGE_FIELDS,
    BUDGET_FIELDS,
    CONVERSION_FIELDS,
    HISTORICAL_FIELDS,
    LOW_QUALITY_FIELDS,
    REVENUE_FIELDS,
    PerformanceReportsMixin,
    ReportsMixin,
)
from suds import sudsobject


class BingAdsBaseStream(Stream, ABC):
    primary_key: Optional[Union[str, List[str], List[List[str]]]] = None

    def __init__(self, client: Client, config: Mapping[str, Any]) -> None:
        super().__init__()
        self.client = client
        self.config = config


class BingAdsStream(BingAdsBaseStream, ABC):
    @property
    @abstractmethod
    def operation_name(self) -> str:
        """
        Specifies operation name to use for a current stream
        """
        pass

    @property
    @abstractmethod
    def service_name(self) -> str:
        """
        Specifies bing ads service name for a current stream
        """
        pass

    @property
    def _service(self) -> Union[ServiceClient, ReportingServiceManager]:
        return self.client.get_service(service_name=self.service_name)

    @property
    def _user_id(self) -> int:
        return self._get_user_id()

    # TODO remove once Microsoft support confirm their SSL certificates are always valid...
    def _get_user_id(self, number_of_retries=10):
        """"""
        try:
            return self._service.GetUser().User.Id
        except URLError as error:
            if isinstance(error.reason, ssl.SSLError):
                self.logger.warning("SSL certificate error, retrying...")
                if number_of_retries > 0:
                    time.sleep(1)
                    return self._get_user_id(number_of_retries - 1)
                else:
                    raise error

    def next_page_token(self, response: sudsobject.Object, **kwargs: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
        """
        Default method for streams that don't support pagination
        """
        return None

    def send_request(self, params: Mapping[str, Any], customer_id: str, account_id: str = None) -> Mapping[str, Any]:
        request_kwargs = {
            "service_name": self.service_name,
            "customer_id": customer_id,
            "account_id": account_id,
            "operation_name": self.operation_name,
            "params": params,
        }
        request = self.client.request(**request_kwargs)
        return request

    def read_records(
        self,
        sync_mode: SyncMode,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
        **kwargs: Mapping[str, Any],
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        next_page_token = None
        account_id = str(stream_slice.get("account_id")) if stream_slice else None
        customer_id = str(stream_slice.get("customer_id")) if stream_slice else None

        while True:
            params = self.request_params(
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
                account_id=account_id,
            )
            response = self.send_request(params, customer_id=customer_id, account_id=account_id)
            for record in self.parse_response(response):
                yield record

            next_page_token = self.next_page_token(response, current_page_token=next_page_token)
            if not next_page_token:
                break

        yield from []

    def parse_response(self, response: sudsobject.Object, **kwargs) -> Iterable[Mapping]:
        if response is not None and hasattr(response, self.data_field):
            yield from self.client.asdict(response)[self.data_field]

        yield from []


class BingAdsCampaignManagementStream(BingAdsStream, ABC):
    service_name: str = "CampaignManagement"

    @property
    @abstractmethod
    def data_field(self) -> str:
        """
        Specifies root object name in a stream response
        """
        pass

    @property
    @abstractmethod
    def additional_fields(self) -> Optional[str]:
        """
        Specifies which additional fields to fetch for a current stream.
        Expected format: field names separated by space
        """
        pass

    def parse_response(self, response: sudsobject.Object, **kwargs) -> Iterable[Mapping]:
        if response is not None and hasattr(response, self.data_field):
            yield from self.client.asdict(response)[self.data_field]

        yield from []


class BingAdsReportingServiceStream(BingAdsStream, ABC):

    cursor_field = "TimePeriod"
    service_name: str = "ReportingService"
    operation_name: str = "download_report"

    def parse_response(self, response: sudsobject.Object, **kwargs: Mapping[str, Any]) -> Iterable[Mapping]:
        if response is not None:
            for row in response.report_records:
                yield {column: self.get_column_value(row, column) for column in self.report_columns}

        yield from []

    @staticmethod
    def get_column_value(row: _RowReportRecord, column: str) -> Union[str, None, int, float]:
        """
        Reads field value from row and transforms:
        1. empty values to logical None
        2. Percent values to numeric string e.g. "12.25%" -> "12.25"
        """
        value = row.value(column)
        if not value or value == "--":
            return None
        if "%" in value:
            value = value.replace("%", "")

        return value


class BingAdsBulkStream(BingAdsBaseStream, IncrementalMixin, ABC):

    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)
    cursor_field = "Modified Time"
    _state = {}

    @property
    @abstractmethod
    def data_scope(self) -> List[str]:
        """
        Defines scopes or types of data to download. Docs: https://learn.microsoft.com/en-us/advertising/bulk-service/datascope?view=bingads-13
        """

    @property
    @abstractmethod
    def download_entities(self) -> List[str]:
        """
        Defines the entities that should be downloaded. Docs: https://learn.microsoft.com/en-us/advertising/bulk-service/downloadentity?view=bingads-13
        """

    def stream_slices(
        self,
        **kwargs: Mapping[str, Any],
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for account in Accounts(self.client, self.config).read_records(SyncMode.full_refresh):
            yield {"account_id": account["Id"], "customer_id": account["ParentCustomerId"]}

        yield from []

    @property
    def state(self) -> Mapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._state.update({str(value["Account Id"]): {self.cursor_field: value[self.cursor_field]}})

    def get_start_date(self, stream_state: Mapping[str, Any] = None, account_id: str = None):
        """
        Start_date in request can be provided only if it is sooner than 30 days from now
        """
        min_available_date = pendulum.now().subtract(days=30).astimezone(tz=timezone.utc)
        start_date = self.client.reports_start_date
        if stream_state.get(account_id, {}).get(self.cursor_field):
            start_date = pendulum.from_format(stream_state[account_id][self.cursor_field], "MM/DD/YYYY HH:mm:ss.SSS")
        return None if start_date < min_available_date else min_available_date

    def read_records(
        self,
        sync_mode: SyncMode,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
        **kwargs: Mapping[str, Any],
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        account_id = str(stream_slice.get("account_id")) if stream_slice else None
        customer_id = str(stream_slice.get("customer_id")) if stream_slice else None

        report_file_path = self.client.get_bulk_entity(
            data_scope=self.data_scope,
            download_entities=self.download_entities,
            customer_id=customer_id,
            account_id=account_id,
            start_date=self.get_start_date(stream_state, account_id),
        )
        for record in self.read_with_chunks(report_file_path):
            record = self.transform(record, stream_slice)
            yield record
            self.state = record

        yield from []

    def read_with_chunks(self, path: str, chunk_size: int = 1024) -> Iterable[Tuple[int, Mapping[str, Any]]]:
        try:
            with open(path, "r") as data:
                chunks = pd.read_csv(data, chunksize=chunk_size, iterator=True, dialect="unix", dtype=object)
                for chunk in chunks:
                    chunk = chunk.replace({nan: None}).to_dict(orient="records")
                    for row in chunk:
                        if row.get("Type") not in ("Format Version", "Account"):
                            yield row
        except pd.errors.EmptyDataError as e:
            self.logger.info(f"Empty data received. {e}")
            yield from []
        except IOError as ioe:
            self.logger.fatal(
                f"The IO/Error occurred while reading tmp data. Called: {path}. Stream: {self.name}",
            )
            raise ioe
        finally:
            # remove binary tmp file, after data is read
            os.remove(path)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        """
        Bing Ads Bulk API returns all available properties for all entities.
        This method filter out only available properties.
        """
        actual_record = {key: value for key, value in record.items() if key in self.get_json_schema()["properties"].keys()}
        actual_record["Account Id"] = stream_slice.get("account_id")
        return actual_record


class AppInstallAds(BingAdsBulkStream):
    """
    https://learn.microsoft.com/en-us/advertising/bulk-service/app-install-ad?view=bingads-13
    """

    data_scope = ["EntityData"]
    download_entities = ["AppInstallAds"]

    primary_key = "Id"


class AppInstallAdLabels(BingAdsBulkStream):
    """
    https://learn.microsoft.com/en-us/advertising/bulk-service/app-install-ad-label?view=bingads-13
    """

    data_scope = ["EntityData"]
    download_entities = ["AppInstallAdLabels"]

    primary_key = "Id"


class Labels(BingAdsBulkStream):
    """
    https://learn.microsoft.com/en-us/advertising/bulk-service/label?view=bingads-13
    """

    data_scope = ["EntityData"]
    download_entities = ["Labels"]

    primary_key = "Id"


class KeywordLabels(BingAdsBulkStream):
    """
    https://learn.microsoft.com/en-us/advertising/bulk-service/keyword-label?view=bingads-13
    """

    data_scope = ["EntityData"]
    download_entities = ["KeywordLabels"]

    primary_key = "Id"


class Keywords(BingAdsBulkStream):
    """
    https://learn.microsoft.com/en-us/advertising/bulk-service/keyword?view=bingads-13
    """

    data_scope = ["EntityData"]
    download_entities = ["Keywords"]

    primary_key = "Id"


class CampaignLabels(BingAdsBulkStream):
    """
    https://learn.microsoft.com/en-us/advertising/bulk-service/campaign-label?view=bingads-13
    """

    data_scope = ["EntityData"]
    download_entities = ["CampaignLabels"]

    primary_key = "Id"


class AdGroupLabels(BingAdsBulkStream):
    """
    https://learn.microsoft.com/en-us/advertising/bulk-service/ad-group-label?view=bingads-13
    """

    data_scope = ["EntityData"]
    download_entities = ["AdGroupLabels"]

    primary_key = "Id"


class Accounts(BingAdsStream):
    """
    Searches for accounts that the current authenticated user can access.
    API doc: https://docs.microsoft.com/en-us/advertising/customer-management-service/searchaccounts?view=bingads-13
    Account schema: https://docs.microsoft.com/en-us/advertising/customer-management-service/advertiseraccount?view=bingads-13
    Stream caches incoming responses to be able to reuse this data in Campaigns stream
    """

    primary_key = "Id"
    # Stream caches incoming responses to avoid duplicated http requests
    use_cache: bool = True
    data_field: str = "AdvertiserAccount"
    service_name: str = "CustomerManagementService"
    operation_name: str = "SearchAccounts"
    additional_fields: str = "TaxCertificate AccountMode"
    # maximum page size
    page_size_limit: int = 1000

    def next_page_token(self, response: sudsobject.Object, current_page_token: Optional[int]) -> Optional[Mapping[str, Any]]:
        current_page_token = current_page_token or 0
        if response is not None and hasattr(response, self.data_field):
            return None if self.page_size_limit > len(response[self.data_field]) else current_page_token + 1
        else:
            return None

    def request_params(
        self,
        next_page_token: Mapping[str, Any] = None,
        **kwargs: Mapping[str, Any],
    ) -> MutableMapping[str, Any]:
        predicates = {
            "Predicate": [
                {
                    "Field": "UserId",
                    "Operator": "Equals",
                    "Value": self._user_id,
                }
            ]
        }

        paging = self._service.factory.create("ns5:Paging")
        paging.Index = next_page_token or 0
        paging.Size = self.page_size_limit
        return {
            "PageInfo": paging,
            "Predicates": predicates,
            "ReturnAdditionalFields": self.additional_fields,
        }


class Campaigns(BingAdsCampaignManagementStream):
    """
    Gets the campaigns for all provided accounts.
    API doc: https://docs.microsoft.com/en-us/advertising/campaign-management-service/getcampaignsbyaccountid?view=bingads-13
    Campaign schema: https://docs.microsoft.com/en-us/advertising/campaign-management-service/campaign?view=bingads-13
    Stream caches incoming responses to be able to reuse this data in AdGroups stream
    """

    primary_key = "Id"
    # Stream caches incoming responses to avoid duplicated http requests
    use_cache: bool = True
    data_field: str = "Campaign"
    operation_name: str = "GetCampaignsByAccountId"
    additional_fields: Iterable[str] = [
        "AdScheduleUseSearcherTimeZone",
        "BidStrategyId",
        "CpvCpmBiddingScheme",
        "DynamicDescriptionSetting",
        "DynamicFeedSetting",
        "MaxConversionValueBiddingScheme",
        "MultimediaAdsBidAdjustment",
        "TargetImpressionShareBiddingScheme",
        "TargetSetting",
        "VerifiedTrackingSetting",
    ]
    campaign_types: Iterable[str] = ["Audience", "DynamicSearchAds", "Search", "Shopping"]

    def request_params(
        self,
        stream_slice: Mapping[str, Any] = None,
        **kwargs: Mapping[str, Any],
    ) -> MutableMapping[str, Any]:
        return {
            "AccountId": stream_slice["account_id"],
            "CampaignType": " ".join(self.campaign_types),
            "ReturnAdditionalFields": " ".join(self.additional_fields),
        }

    def stream_slices(
        self,
        **kwargs: Mapping[str, Any],
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for account in Accounts(self.client, self.config).read_records(SyncMode.full_refresh):
            yield {"account_id": account["Id"], "customer_id": account["ParentCustomerId"]}

        yield from []


class AdGroups(BingAdsCampaignManagementStream):
    """
    Gets the ad groups for all provided accounts.
    API doc: https://docs.microsoft.com/en-us/advertising/campaign-management-service/getadgroupsbycampaignid?view=bingads-13
    AdGroup schema: https://docs.microsoft.com/en-us/advertising/campaign-management-service/adgroup?view=bingads-13
    Stream caches incoming responses to be able to reuse this data in Ads stream
    """

    primary_key = "Id"
    # Stream caches incoming responses to avoid duplicated http requests
    use_cache: bool = True
    data_field: str = "AdGroup"
    operation_name: str = "GetAdGroupsByCampaignId"
    additional_fields: str = "AdGroupType AdScheduleUseSearcherTimeZone CpmBid CpvBid MultimediaAdsBidAdjustment"

    def request_params(
        self,
        stream_slice: Mapping[str, Any] = None,
        **kwargs: Mapping[str, Any],
    ) -> MutableMapping[str, Any]:
        return {"CampaignId": stream_slice["campaign_id"], "ReturnAdditionalFields": self.additional_fields}

    def stream_slices(
        self,
        **kwargs: Mapping[str, Any],
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        campaigns = Campaigns(self.client, self.config)
        for account in Accounts(self.client, self.config).read_records(SyncMode.full_refresh):
            for campaign in campaigns.read_records(
                sync_mode=SyncMode.full_refresh, stream_slice={"account_id": account["Id"], "customer_id": account["ParentCustomerId"]}
            ):
                yield {"campaign_id": campaign["Id"], "account_id": account["Id"], "customer_id": account["ParentCustomerId"]}

        yield from []


class Ads(BingAdsCampaignManagementStream):
    """
    Retrieves the ads for all provided accounts.
    API doc: https://docs.microsoft.com/en-us/advertising/campaign-management-service/getadsbyadgroupid?view=bingads-13
    Ad schema: https://docs.microsoft.com/en-us/advertising/campaign-management-service/ad?view=bingads-13
    """

    primary_key = "Id"
    data_field: str = "Ad"
    operation_name: str = "GetAdsByAdGroupId"
    additional_fields: str = "ImpressionTrackingUrls Videos LongHeadlines"
    ad_types: Iterable[str] = [
        "Text",
        "Image",
        "Product",
        "AppInstall",
        "ExpandedText",
        "DynamicSearch",
        "ResponsiveAd",
        "ResponsiveSearch",
    ]

    def request_params(
        self,
        stream_slice: Mapping[str, Any] = None,
        **kwargs: Mapping[str, Any],
    ) -> MutableMapping[str, Any]:
        return {
            "AdGroupId": stream_slice["ad_group_id"],
            "AdTypes": {"AdType": self.ad_types},
            "ReturnAdditionalFields": self.additional_fields,
        }

    def stream_slices(
        self,
        **kwargs: Mapping[str, Any],
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        ad_groups = AdGroups(self.client, self.config)
        for slice in ad_groups.stream_slices(sync_mode=SyncMode.full_refresh):
            for ad_group in ad_groups.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice):
                yield {"ad_group_id": ad_group["Id"], "account_id": slice["account_id"], "customer_id": slice["customer_id"]}
        yield from []


class BudgetSummaryReport(ReportsMixin, BingAdsReportingServiceStream):
    report_name: str = "BudgetSummaryReport"
    report_aggregation = None
    cursor_field = "Date"
    report_schema_name = "budget_summary_report"
    primary_key = "Date"

    report_columns = [
        "AccountName",
        "AccountNumber",
        "AccountId",
        "CampaignName",
        "CampaignId",
        "Date",
        "MonthlyBudget",
        "DailySpend",
        "MonthToDateSpend",
    ]


class CampaignPerformanceReport(PerformanceReportsMixin, BingAdsReportingServiceStream):
    report_name: str = "CampaignPerformanceReport"

    report_schema_name = "campaign_performance_report"
    primary_key = [
        "AccountId",
        "CampaignId",
        "TimePeriod",
        "CurrencyCode",
        "AdDistribution",
        "DeviceType",
        "Network",
        "DeliveredMatchType",
        "DeviceOS",
        "TopVsOther",
        "BidMatchType",
    ]

    report_columns = [
        *primary_key,
        "AccountName",
        "CampaignName",
        "CampaignType",
        "CampaignStatus",
        "CampaignLabels",
        "Impressions",
        "Clicks",
        "Ctr",
        "Spend",
        "CostPerConversion",
        "QualityScore",
        "AdRelevance",
        "LandingPageExperience",
        "PhoneImpressions",
        "PhoneCalls",
        "Ptr",
        "Assists",
        "ReturnOnAdSpend",
        "CostPerAssist",
        "CustomParameters",
        "ViewThroughConversions",
        "AllCostPerConversion",
        "AllReturnOnAdSpend",
        *ALL_CONVERSION_FIELDS,
        *ALL_REVENUE_FIELDS,
        *AVERAGE_FIELDS,
        *CONVERSION_FIELDS,
        *LOW_QUALITY_FIELDS,
        *REVENUE_FIELDS,
        *BUDGET_FIELDS,
    ]


class CampaignPerformanceReportHourly(CampaignPerformanceReport):
    report_aggregation = "Hourly"


class CampaignPerformanceReportDaily(CampaignPerformanceReport):
    report_aggregation = "Daily"
    report_columns = [
        *CampaignPerformanceReport.report_columns,
        *HISTORICAL_FIELDS,
    ]


class CampaignPerformanceReportWeekly(CampaignPerformanceReport):
    report_aggregation = "Weekly"
    report_columns = [
        *CampaignPerformanceReport.report_columns,
        *HISTORICAL_FIELDS,
    ]


class CampaignPerformanceReportMonthly(CampaignPerformanceReport):
    report_aggregation = "Monthly"
    report_columns = [
        *CampaignPerformanceReport.report_columns,
        *HISTORICAL_FIELDS,
    ]


class CampaignImpressionPerformanceReport(PerformanceReportsMixin, BingAdsReportingServiceStream, ABC):
    """
    https://learn.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13
    Primary key cannot be set: due to included `Impression Share Performance Statistics` some fields should be removed,
    see https://learn.microsoft.com/en-us/advertising/guides/reports?view=bingads-13#columnrestrictions for more info.
    """

    report_name: str = "CampaignPerformanceReport"

    report_schema_name = "campaign_impression_performance_report"

    primary_key = None

    @property
    def report_columns(self) -> Iterable[str]:
        return list(self.get_json_schema().get("properties", {}).keys())


class CampaignImpressionPerformanceReportHourly(CampaignImpressionPerformanceReport):
    report_aggregation = "Hourly"

    report_schema_name = "campaign_impression_performance_report_hourly"


class CampaignImpressionPerformanceReportDaily(CampaignImpressionPerformanceReport):
    report_aggregation = "Daily"


class CampaignImpressionPerformanceReportWeekly(CampaignImpressionPerformanceReport):
    report_aggregation = "Weekly"


class CampaignImpressionPerformanceReportMonthly(CampaignImpressionPerformanceReport):
    report_aggregation = "Monthly"


class AdPerformanceReport(PerformanceReportsMixin, BingAdsReportingServiceStream):
    report_name: str = "AdPerformanceReport"

    report_schema_name = "ad_performance_report"
    primary_key = [
        "AccountId",
        "CampaignId",
        "AdGroupId",
        "AdId",
        "TimePeriod",
        "CurrencyCode",
        "AdDistribution",
        "DeviceType",
        "Language",
        "Network",
        "DeviceOS",
        "TopVsOther",
        "BidMatchType",
        "DeliveredMatchType",
    ]

    report_columns = [
        *primary_key,
        "AccountName",
        "CampaignName",
        "CampaignType",
        "AdGroupName",
        "Impressions",
        "Clicks",
        "Ctr",
        "Spend",
        "CostPerConversion",
        "DestinationUrl",
        "Assists",
        "ReturnOnAdSpend",
        "CostPerAssist",
        "CustomParameters",
        "FinalAppUrl",
        "AdDescription",
        "AdDescription2",
        "ViewThroughConversions",
        "ViewThroughConversionsQualified",
        "AllCostPerConversion",
        "AllReturnOnAdSpend",
        *CONVERSION_FIELDS,
        *AVERAGE_FIELDS,
        *ALL_CONVERSION_FIELDS,
        *ALL_REVENUE_FIELDS,
        *REVENUE_FIELDS,
    ]


class AdPerformanceReportHourly(AdPerformanceReport):
    report_aggregation = "Hourly"


class AdPerformanceReportDaily(AdPerformanceReport):
    report_aggregation = "Daily"


class AdPerformanceReportWeekly(AdPerformanceReport):
    report_aggregation = "Weekly"


class AdPerformanceReportMonthly(AdPerformanceReport):
    report_aggregation = "Monthly"


class AdGroupPerformanceReport(PerformanceReportsMixin, BingAdsReportingServiceStream, ABC):
    report_name: str = "AdGroupPerformanceReport"

    report_schema_name = "ad_group_performance_report"

    primary_key = [
        "AccountId",
        "CampaignId",
        "AdGroupId",
        "TimePeriod",
        "CurrencyCode",
        "AdDistribution",
        "DeviceType",
        "Network",
        "DeliveredMatchType",
        "DeviceOS",
        "TopVsOther",
        "BidMatchType",
        "Language",
    ]

    report_columns = [
        *primary_key,
        "AccountName",
        "CampaignName",
        "CampaignType",
        "AdGroupName",
        "AdGroupType",
        "Impressions",
        "Clicks",
        "Ctr",
        "Spend",
        "CostPerConversion",
        "QualityScore",
        "ExpectedCtr",
        "AdRelevance",
        "LandingPageExperience",
        "PhoneImpressions",
        "PhoneCalls",
        "Ptr",
        "Assists",
        "CostPerAssist",
        "CustomParameters",
        "FinalUrlSuffix",
        "ViewThroughConversions",
        "AllCostPerConversion",
        "AllReturnOnAdSpend",
        *ALL_CONVERSION_FIELDS,
        *ALL_REVENUE_FIELDS,
        *AVERAGE_FIELDS,
        *CONVERSION_FIELDS,
        *REVENUE_FIELDS,
    ]


class AdGroupPerformanceReportHourly(AdGroupPerformanceReport):
    report_aggregation = "Hourly"


class AdGroupPerformanceReportDaily(AdGroupPerformanceReport):
    report_aggregation = "Daily"
    report_columns = [
        *AdGroupPerformanceReport.report_columns,
        *HISTORICAL_FIELDS,
    ]


class AdGroupPerformanceReportWeekly(AdGroupPerformanceReport):
    report_aggregation = "Weekly"
    report_columns = [
        *AdGroupPerformanceReport.report_columns,
        *HISTORICAL_FIELDS,
    ]


class AdGroupPerformanceReportMonthly(AdGroupPerformanceReport):
    report_aggregation = "Monthly"
    report_columns = [
        *AdGroupPerformanceReport.report_columns,
        *HISTORICAL_FIELDS,
    ]


class AdGroupImpressionPerformanceReport(PerformanceReportsMixin, BingAdsReportingServiceStream, ABC):
    """
    https://learn.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13
    Primary key cannot be set: due to included `Impression Share Performance Statistics` some fields should be removed,
    see https://learn.microsoft.com/en-us/advertising/guides/reports?view=bingads-13#columnrestrictions for more info.
    """

    report_name: str = "AdGroupPerformanceReport"

    report_schema_name = "ad_group_impression_performance_report"

    @property
    def report_columns(self) -> Iterable[str]:
        return list(self.get_json_schema().get("properties", {}).keys())


class AdGroupImpressionPerformanceReportHourly(AdGroupImpressionPerformanceReport):
    report_aggregation = "Hourly"
    report_schema_name = "ad_group_impression_performance_report_hourly"


class AdGroupImpressionPerformanceReportDaily(AdGroupImpressionPerformanceReport):
    report_aggregation = "Daily"


class AdGroupImpressionPerformanceReportWeekly(AdGroupImpressionPerformanceReport):
    report_aggregation = "Weekly"


class AdGroupImpressionPerformanceReportMonthly(AdGroupImpressionPerformanceReport):
    report_aggregation = "Monthly"


class KeywordPerformanceReport(PerformanceReportsMixin, BingAdsReportingServiceStream, ABC):

    report_name: str = "KeywordPerformanceReport"

    report_schema_name = "keyword_performance_report"
    primary_key = [
        "AccountId",
        "CampaignId",
        "AdGroupId",
        "KeywordId",
        "AdId",
        "TimePeriod",
        "CurrencyCode",
        "DeliveredMatchType",
        "AdDistribution",
        "DeviceType",
        "Language",
        "Network",
        "DeviceOS",
        "TopVsOther",
        "BidMatchType",
    ]

    report_columns = [
        *primary_key,
        "AccountName",
        "CampaignName",
        "AdGroupName",
        "Keyword",
        "KeywordStatus",
        "Impressions",
        "Clicks",
        "Ctr",
        "CurrentMaxCpc",
        "Spend",
        "CostPerConversion",
        "QualityScore",
        "ExpectedCtr",
        "AdRelevance",
        "LandingPageExperience",
        "QualityImpact",
        "Assists",
        "ReturnOnAdSpend",
        "CostPerAssist",
        "CustomParameters",
        "FinalAppUrl",
        "Mainline1Bid",
        "MainlineBid",
        "FirstPageBid",
        "FinalUrlSuffix",
        "ViewThroughConversions",
        "ViewThroughConversionsQualified",
        "AllCostPerConversion",
        "AllReturnOnAdSpend",
        *CONVERSION_FIELDS,
        *AVERAGE_FIELDS,
        *ALL_CONVERSION_FIELDS,
        *ALL_REVENUE_FIELDS,
        *REVENUE_FIELDS,
    ]


class KeywordPerformanceReportHourly(KeywordPerformanceReport):
    report_aggregation = "Hourly"


class KeywordPerformanceReportDaily(KeywordPerformanceReport):
    report_aggregation = "Daily"
    report_columns = [
        *KeywordPerformanceReport.report_columns,
        *HISTORICAL_FIELDS,
    ]


class KeywordPerformanceReportWeekly(KeywordPerformanceReport):
    report_aggregation = "Weekly"


class KeywordPerformanceReportMonthly(KeywordPerformanceReport):
    report_aggregation = "Monthly"


class GeographicPerformanceReport(PerformanceReportsMixin, BingAdsReportingServiceStream, ABC):

    report_name: str = "GeographicPerformanceReport"

    report_schema_name = "geographic_performance_report"

    # Need to override the primary key here because the one inherited from the PerformanceReportsMixin
    # is incorrect for the geographic performance reports
    primary_key = None

    report_columns = [
        "AccountId",
        "CampaignId",
        "AdGroupId",
        "TimePeriod",
        "Country",
        "CurrencyCode",
        "DeliveredMatchType",
        "AdDistribution",
        "DeviceType",
        "Language",
        "Network",
        "DeviceOS",
        "TopVsOther",
        "BidMatchType",
        "MetroArea",
        "State",
        "City",
        "AdGroupName",
        "Ctr",
        "ProximityTargetLocation",
        "Radius",
        "Assists",
        "ReturnOnAdSpend",
        "CostPerAssist",
        "LocationType",
        "MostSpecificLocation",
        "AccountStatus",
        "CampaignStatus",
        "AdGroupStatus",
        "County",
        "PostalCode",
        "LocationId",
        "BaseCampaignId",
        "AllCostPerConversion",
        "AllReturnOnAdSpend",
        "ViewThroughConversions",
        "Goal",
        "GoalType",
        "AbsoluteTopImpressionRatePercent",
        "TopImpressionRatePercent",
        "AllConversionsQualified",
        "ViewThroughConversionsQualified",
        "Neighborhood",
        "ViewThroughRevenue",
        "CampaignType",
        "AssetGroupId",
        "AssetGroupName",
        "AssetGroupStatus",
        "Clicks",
        "Spend",
        "Impressions",
        "CostPerConversion",
        "AccountName",
        "AccountNumber",
        "CampaignName",
        *CONVERSION_FIELDS,
        *AVERAGE_FIELDS,
        *ALL_CONVERSION_FIELDS,
        *ALL_REVENUE_FIELDS,
        *REVENUE_FIELDS,
    ]


class GeographicPerformanceReportHourly(GeographicPerformanceReport):
    report_aggregation = "Hourly"


class GeographicPerformanceReportDaily(GeographicPerformanceReport):
    report_aggregation = "Daily"


class GeographicPerformanceReportWeekly(GeographicPerformanceReport):
    report_aggregation = "Weekly"


class GeographicPerformanceReportMonthly(GeographicPerformanceReport):
    report_aggregation = "Monthly"


class AccountPerformanceReport(PerformanceReportsMixin, BingAdsReportingServiceStream):

    report_name: str = "AccountPerformanceReport"

    report_schema_name = "account_performance_report"
    primary_key = [
        "AccountId",
        "TimePeriod",
        "CurrencyCode",
        "AdDistribution",
        "DeviceType",
        "Network",
        "DeliveredMatchType",
        "DeviceOS",
        "TopVsOther",
        "BidMatchType",
    ]

    report_columns = [
        *primary_key,
        "AccountName",
        "AccountNumber",
        "PhoneImpressions",
        "PhoneCalls",
        "Clicks",
        "Ctr",
        "Spend",
        "Impressions",
        "CostPerConversion",
        "Ptr",
        "Assists",
        "ReturnOnAdSpend",
        "CostPerAssist",
        *AVERAGE_FIELDS,
        *CONVERSION_FIELDS,
        *LOW_QUALITY_FIELDS,
        *REVENUE_FIELDS,
    ]


class AccountPerformanceReportHourly(AccountPerformanceReport):
    report_aggregation = "Hourly"


class AccountPerformanceReportDaily(AccountPerformanceReport):
    report_aggregation = "Daily"


class AccountPerformanceReportWeekly(AccountPerformanceReport):
    report_aggregation = "Weekly"


class AccountPerformanceReportMonthly(AccountPerformanceReport):
    report_aggregation = "Monthly"


class AccountImpressionPerformanceReport(PerformanceReportsMixin, BingAdsReportingServiceStream, ABC):
    """
    Report source: https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13
    Primary key cannot be set: due to included `Impression Share Performance Statistics` some fields should be removed,
    see https://learn.microsoft.com/en-us/advertising/guides/reports?view=bingads-13#columnrestrictions for more info.
    """

    report_name: str = "AccountPerformanceReport"
    report_schema_name = "account_impression_performance_report"
    primary_key = None

    @property
    def report_columns(self):
        return list(self.get_json_schema().get("properties", {}).keys())


class AccountImpressionPerformanceReportHourly(AccountImpressionPerformanceReport):
    report_aggregation = "Hourly"

    report_schema_name = "account_impression_performance_report_hourly"


class AccountImpressionPerformanceReportDaily(AccountImpressionPerformanceReport):
    report_aggregation = "Daily"


class AccountImpressionPerformanceReportWeekly(AccountImpressionPerformanceReport):
    report_aggregation = "Weekly"


class AccountImpressionPerformanceReportMonthly(AccountImpressionPerformanceReport):
    report_aggregation = "Monthly"


class AgeGenderAudienceReport(PerformanceReportsMixin, BingAdsReportingServiceStream, ABC):

    report_name: str = "AgeGenderAudienceReport"

    report_schema_name = "age_gender_audience_report"
    primary_key = ["AgeGroup", "Gender", "TimePeriod", "AccountId", "CampaignId", "Language", "AdDistribution"]

    @property
    def report_columns(self):
        return list(self.get_json_schema().get("properties", {}).keys())


class AgeGenderAudienceReportHourly(AgeGenderAudienceReport):
    report_aggregation = "Hourly"


class AgeGenderAudienceReportDaily(AgeGenderAudienceReport):
    report_aggregation = "Daily"


class AgeGenderAudienceReportWeekly(AgeGenderAudienceReport):
    report_aggregation = "Weekly"


class AgeGenderAudienceReportMonthly(AgeGenderAudienceReport):
    report_aggregation = "Monthly"


class SearchQueryPerformanceReport(PerformanceReportsMixin, BingAdsReportingServiceStream, ABC):

    report_name: str = "SearchQueryPerformanceReport"

    report_schema_name = "search_query_performance_report"
    primary_key = [
        "SearchQuery",
        "Keyword",
        "TimePeriod",
        "AccountId",
        "CampaignId",
        "Language",
        "DeliveredMatchType",
        "DeviceType",
        "DeviceOS",
        "TopVsOther",
    ]

    @property
    def report_columns(self) -> List[str]:
        return list(self.get_json_schema().get("properties", {}).keys())


class SearchQueryPerformanceReportHourly(SearchQueryPerformanceReport):
    report_aggregation = "Hourly"


class SearchQueryPerformanceReportDaily(SearchQueryPerformanceReport):
    report_aggregation = "Daily"


class SearchQueryPerformanceReportWeekly(SearchQueryPerformanceReport):
    report_aggregation = "Weekly"


class SearchQueryPerformanceReportMonthly(SearchQueryPerformanceReport):
    report_aggregation = "Monthly"


class UserLocationPerformanceReport(PerformanceReportsMixin, BingAdsReportingServiceStream, ABC):

    report_name: str = "UserLocationPerformanceReport"
    report_schema_name = "user_location_performance_report"
    primary_key = [
        "AccountId",
        "AdGroupId",
        "CampaignId",
        "DeliveredMatchType",
        "DeviceOS",
        "DeviceType",
        "Language",
        "LocationId",
        "QueryIntentLocationId",
        "TimePeriod",
        "TopVsOther",
    ]

    @property
    def report_columns(self) -> List[str]:
        return list(self.get_json_schema().get("properties", {}).keys())


class UserLocationPerformanceReportHourly(UserLocationPerformanceReport):
    report_aggregation = "Hourly"


class UserLocationPerformanceReportDaily(UserLocationPerformanceReport):
    report_aggregation = "Daily"


class UserLocationPerformanceReportWeekly(UserLocationPerformanceReport):
    report_aggregation = "Weekly"


class UserLocationPerformanceReportMonthly(UserLocationPerformanceReport):
    report_aggregation = "Monthly"
