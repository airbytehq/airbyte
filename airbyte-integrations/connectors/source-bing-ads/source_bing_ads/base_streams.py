#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import ssl
import time
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union
from urllib.error import URLError

from bingads.service_client import ServiceClient
from bingads.v13.reporting.reporting_service_manager import ReportingServiceManager
from suds import sudsobject

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from source_bing_ads.client import Client


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

    @property
    @abstractmethod
    def service_name(self) -> str:
        """
        Specifies bing ads service name for a current stream
        """

    @property
    def parent_key_to_foreign_key_map(self) -> MutableMapping[str, str]:
        """
        Specifies dict with field in record as kay and slice key as value to be inserted in record in transform method.
        """
        return {}

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        foreign_keys = {key: stream_slice.get(value) for key, value in self.parent_key_to_foreign_key_map.items()}
        return record | foreign_keys

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
                yield self.transform(record, stream_slice)

            next_page_token = self.next_page_token(response, current_page_token=next_page_token)
            if not next_page_token:
                break

    def parse_response(self, response: sudsobject.Object, **kwargs) -> Iterable[Mapping]:
        if response is not None and hasattr(response, self.data_field):
            yield from self.client.asdict(response)[self.data_field]


class BingAdsCampaignManagementStream(BingAdsStream, ABC):
    service_name: str = "CampaignManagement"

    @property
    @abstractmethod
    def data_field(self) -> str:
        """
        Specifies root object name in a stream response
        """

    @property
    @abstractmethod
    def additional_fields(self) -> Optional[str]:
        """
        Specifies which additional fields to fetch for a current stream.
        Expected format: field names separated by space
        """

    def parse_response(self, response: sudsobject.Object, **kwargs) -> Iterable[Mapping]:
        if response is not None and hasattr(response, self.data_field):
            yield from self.client.asdict(response)[self.data_field]


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

    def __init__(self, client: Client, config: Mapping[str, Any]) -> None:
        super().__init__(client, config)
        self._account_names = config.get("account_names", [])
        self._unique_account_ids = set()

    def next_page_token(self, response: sudsobject.Object, current_page_token: Optional[int]) -> Optional[Mapping[str, Any]]:
        current_page_token = current_page_token or 0
        if response is not None and hasattr(response, self.data_field):
            return None if self.page_size_limit > len(response[self.data_field]) else current_page_token + 1
        else:
            return None

    def stream_slices(
        self,
        **kwargs: Mapping[str, Any],
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        user_id_predicate = {
            "Field": "UserId",
            "Operator": "Equals",
            "Value": self._user_id,
        }
        if self._account_names:
            for account_config in self._account_names:
                account_name_predicate = {"Field": "AccountName", "Operator": account_config["operator"], "Value": account_config["name"]}

                yield {"predicates": {"Predicate": [user_id_predicate, account_name_predicate]}}
        else:
            yield {"predicates": {"Predicate": [user_id_predicate]}}

    def request_params(
        self,
        next_page_token: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        **kwargs: Mapping[str, Any],
    ) -> MutableMapping[str, Any]:
        paging = self._service.factory.create("ns5:Paging")
        paging.Index = next_page_token or 0
        paging.Size = self.page_size_limit
        return {
            "PageInfo": paging,
            "Predicates": stream_slice["predicates"],
            "ReturnAdditionalFields": self.additional_fields,
        }

    def _transform_tax_fields(self, record: Mapping[str, Any]) -> Mapping[str, Any]:
        tax_certificates = record["TaxCertificate"].get("TaxCertificates", {}) if record.get("TaxCertificate") is not None else {}
        if tax_certificates and not isinstance(tax_certificates, list):
            tax_certificate_pairs = tax_certificates.get("KeyValuePairOfstringbase64Binary")
            if tax_certificate_pairs:
                record["TaxCertificate"]["TaxCertificates"] = tax_certificate_pairs
        return record

    def parse_response(self, response: sudsobject.Object, **kwargs) -> Iterable[Mapping]:
        if response is not None and hasattr(response, self.data_field):
            records = self.client.asdict(response)[self.data_field]
            for record in records:
                if record["Id"] not in self._unique_account_ids:
                    self._unique_account_ids.add(record["Id"])
                    yield self._transform_tax_fields(record)


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
    campaign_types: Iterable[str] = ["Audience", "DynamicSearchAds", "Search", "Shopping", "PerformanceMax"]

    parent_key_to_foreign_key_map = {
        "AccountId": "account_id",
        "CustomerId": "customer_id",
    }

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
        accounts = Accounts(self.client, self.config)
        for _slice in accounts.stream_slices():
            for account in accounts.read_records(SyncMode.full_refresh, _slice):
                yield {"account_id": account["Id"], "customer_id": account["ParentCustomerId"]}


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

    parent_key_to_foreign_key_map = {"CampaignId": "campaign_id", "AccountId": "account_id", "CustomerId": "customer_id"}

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
        accounts = Accounts(self.client, self.config)
        for _slice in accounts.stream_slices():
            for account in accounts.read_records(SyncMode.full_refresh, _slice):
                for campaign in campaigns.read_records(
                    sync_mode=SyncMode.full_refresh, stream_slice={"account_id": account["Id"], "customer_id": account["ParentCustomerId"]}
                ):
                    yield {"campaign_id": campaign["Id"], "account_id": account["Id"], "customer_id": account["ParentCustomerId"]}


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

    parent_key_to_foreign_key_map = {"AdGroupId": "ad_group_id", "AccountId": "account_id", "CustomerId": "customer_id"}

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
