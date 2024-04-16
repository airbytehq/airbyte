#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import logging
from typing import Any, Iterable, List, Mapping, Optional, Set, Tuple

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from facebook_business.adobjects.adaccount import AdAccount as FBAdAccount
from facebook_business.adobjects.adimage import AdImage
from facebook_business.adobjects.user import User
from facebook_business.exceptions import FacebookRequestError
from source_facebook_marketing.spec import ValidAdSetStatuses, ValidAdStatuses, ValidCampaignStatuses

from .base_insight_streams import AdsInsights
from .base_streams import FBMarketingIncrementalStream, FBMarketingReversedIncrementalStream, FBMarketingStream

logger = logging.getLogger("airbyte")


def fetch_thumbnail_data_url(url: str) -> Optional[str]:
    """Request thumbnail image and return it embedded into the data-link"""
    try:
        response = requests.get(url)
        if response.status_code == requests.status_codes.codes.OK:
            _type = response.headers["content-type"]
            data = base64.b64encode(response.content)
            return f"data:{_type};base64,{data.decode('ascii')}"
        else:
            logger.warning(f"Got {repr(response)} while requesting thumbnail image.")
    except Exception as exc:
        logger.warning(f"Got {str(exc)} while requesting thumbnail image: {url}.")
    return None


class AdCreatives(FBMarketingStream):
    """AdCreative is append-only stream
    doc: https://developers.facebook.com/docs/marketing-api/reference/ad-creative
    """

    entity_prefix = "adcreative"

    def __init__(self, fetch_thumbnail_images: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._fetch_thumbnail_images = fetch_thumbnail_images

    def fields(self, **kwargs) -> List[str]:
        """Remove "thumbnail_data_url" field because it is a computed field, and it's not a field that we can request from Facebook"""
        if self._fields:
            return self._fields

        self._fields = [f for f in super().fields(**kwargs) if f != "thumbnail_data_url"]
        return self._fields

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read with super method and append thumbnail_data_url if enabled"""
        for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
            if self._fetch_thumbnail_images:
                thumbnail_url = record.get("thumbnail_url")
                if thumbnail_url:
                    record["thumbnail_data_url"] = fetch_thumbnail_data_url(thumbnail_url)
            yield record

    def list_objects(self, account_ids_with_state: List[Tuple[str, any]]) -> Iterable:
        return self._get_object_list_parallel(api_call_wrapper=AdCreatives.get_ad_creatives, account_ids_with_state=account_ids_with_state)

    @staticmethod
    def get_ad_creatives(account: FBAdAccount, account_id, fields, params):
        return [FBMarketingStream.add_account_id(record, account_id) for record in account.get_ad_creatives(fields=fields, params=params)]


class CustomConversions(FBMarketingStream):
    """doc: https://developers.facebook.com/docs/marketing-api/reference/custom-conversion"""

    entity_prefix = "customconversion"

    def list_objects(self, account_ids_with_state: List[Tuple[str, any]]) -> Iterable:
        return self._get_object_list_parallel(api_call_wrapper=CustomConversions.get_custom_conversions, account_ids_with_state=account_ids_with_state)

    @staticmethod
    def get_custom_conversions(account: FBAdAccount, account_id, fields, params):
        return [FBMarketingStream.add_account_id(record, account_id) for record in account.get_custom_conversions(fields=fields, params=params)]

class CustomAudiences(FBMarketingStream):
    """doc: https://developers.facebook.com/docs/marketing-api/reference/custom-audience"""

    entity_prefix = "customaudience"
    # The `rule` field is excluded from the list because it caused the error message "Please reduce the amount of data" for certain connections.
    # https://github.com/airbytehq/oncall/issues/2765
    fields_exceptions = ["rule"]

    def list_objects(self, account_ids_with_state: List[Tuple[str, any]]) -> Iterable:
        return self._get_object_list_parallel(api_call_wrapper=CustomAudiences.get_custom_audiences, account_ids_with_state=account_ids_with_state)

    @staticmethod
    def get_custom_audiences(account: FBAdAccount, account_id, fields, params):
        return [FBMarketingStream.add_account_id(record, account_id) for record in account.get_custom_audiences(fields=fields, params=params)]


class Ads(FBMarketingIncrementalStream):
    """doc: https://developers.facebook.com/docs/marketing-api/reference/adgroup"""

    entity_prefix = "ad"
    status_field = "effective_status"
    valid_statuses = [status.value for status in ValidAdStatuses]

    def list_objects(self, account_ids_with_state: List[Tuple[str, any]]) -> Iterable:
        return self._get_object_list_parallel(api_call_wrapper=Ads.get_ads, account_ids_with_state=account_ids_with_state)

    @staticmethod
    def get_ads(account: FBAdAccount, account_id, fields, params):
        return [FBMarketingStream.add_account_id(record, account_id) for record in account.get_ads(fields=fields, params=params)]


class AdRuleLibraries(FBMarketingIncrementalStream):
    """doc: https://developers.facebook.com/docs/marketing-api/ad-rules/guides/trigger-based-rules"""

    entity_prefix = "ad_rule_libraries"

    def list_objects(self, account_ids_with_state: List[Tuple[str, any]]) -> Iterable:
        return self._get_object_list_parallel(api_call_wrapper=AdRuleLibraries.get_ad_rule_libraries, account_ids_with_state=account_ids_with_state)

    @staticmethod
    def get_ad_rule_libraries(account: FBAdAccount, account_id, fields, params):
        return [FBMarketingStream.add_account_id(record, account_id) for record in account.get_ad_rules_library(fields=fields, params=params)]


class AdSets(FBMarketingIncrementalStream):
    """doc: https://developers.facebook.com/docs/marketing-api/reference/ad-campaign"""

    entity_prefix = "adset"
    status_field = "effective_status"
    valid_statuses = [status.value for status in ValidAdSetStatuses]

    def list_objects(self, account_ids_with_state: List[Tuple[str, any]]) -> Iterable:
        return self._get_object_list_parallel(api_call_wrapper=AdSets.get_ad_sets, account_ids_with_state=account_ids_with_state)

    @staticmethod
    def get_ad_sets(account: FBAdAccount, account_id, fields, params):
        return [FBMarketingStream.add_account_id(record, account_id) for record in account.get_ad_sets(fields=fields, params=params)]


class Campaigns(FBMarketingIncrementalStream):
    """doc: https://developers.facebook.com/docs/marketing-api/reference/ad-campaign-group"""

    entity_prefix = "campaign"
    status_field = "effective_status"
    valid_statuses = [status.value for status in ValidCampaignStatuses]

    def list_objects(self, account_ids_with_state: List[Tuple[str, any]]) -> Iterable:
        return self._get_object_list_parallel(api_call_wrapper=Campaigns.get_campaigns, account_ids_with_state=account_ids_with_state)

    @staticmethod
    def get_campaigns(account: FBAdAccount, account_id, fields, params):
        return [FBMarketingStream.add_account_id(record, account_id) for record in account.get_campaigns(fields=fields, params=params)]


class Activities(FBMarketingIncrementalStream):
    """doc: https://developers.facebook.com/docs/marketing-api/reference/ad-activity"""

    entity_prefix = "activity"
    cursor_field = "event_time"
    primary_key = None

    def fields(self, **kwargs) -> List[str]:
        """Remove account_id from fields as cannot be requested, but it is part of schema as foreign key, will be added during processing"""
        if self._fields:
            return self._fields

        self._fields = [f for f in super().fields(**kwargs) if f != "account_id"]
        return self._fields

    def list_objects(self, account_ids_with_state: List[Tuple[str, any]]) -> Iterable:
        return self._get_object_list_parallel(api_call_wrapper=Activities.get_activities, account_ids_with_state=account_ids_with_state)

    @staticmethod
    def get_activities(account: FBAdAccount, account_id, fields, params):
        return [FBMarketingStream.add_account_id(record, account_id) for record in account.get_activities(fields=fields, params=params)]

    def _state_filter(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        """Additional filters associated with state if any set"""
        state_value = stream_state.get(self.cursor_field)
        if stream_state:
            since = pendulum.parse(state_value)
        elif self._start_date:
            since = self._start_date
        else:
            # if start_date is not specified then do not use date filters
            return {}

        potentially_new_records_in_the_past = self._filter_statuses and (
            set(self._filter_statuses) - set(stream_state.get("filter_statuses", []))
        )
        if potentially_new_records_in_the_past:
            self.logger.info(f"Ignoring bookmark for {self.name} because of enabled `filter_statuses` option")
            if self._start_date:
                since = self._start_date
            else:
                # if start_date is not specified then do not use date filters
                return {}

        return {"since": since.int_timestamp}


class Videos(FBMarketingReversedIncrementalStream):
    """See: https://developers.facebook.com/docs/marketing-api/reference/video"""

    entity_prefix = "video"

    def fields(self, **kwargs) -> List[str]:
        """Remove account_id from fields as cannot be requested, but it is part of schema as foreign key, will be added during processing"""
        if self._fields:
            return self._fields

        self._fields = [f for f in super().fields() if f != "account_id"]
        return self._fields

    def list_objects(self, account_ids_with_state: List[Tuple[str, any]]) -> Iterable:
        return self._get_object_list_parallel(api_call_wrapper=Videos.get_videos, account_ids_with_state=account_ids_with_state)

    @staticmethod
    def get_videos(account: FBAdAccount, account_id, fields, params):
        return [FBMarketingStream.add_account_id(record, account_id) for record in account.get_ad_videos(fields=fields, params=params)]


class AdAccounts(FBMarketingStream):
    """See: https://developers.facebook.com/docs/marketing-api/reference/ad-account"""

    use_batch = False
    fields_exceptions = [
        "business",
        "business_street",
        "business_street2",
        "capabilities",
        "failed_delivery_checks",
        "has_migrated_permissions",
        "extended_credit_invoice_group",
        "failed_delivery_checks",
        "funding_source",
        "funding_source_details",
        "offsite_pixels_tos_accepted",
        "owner",
        "tos_accepted",
        "user_tasks",
        "user_tos_accepted",
    ]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._fields_dict = {}

    def get_task_permissions(self, account_id: str) -> Set[str]:
        """https://developers.facebook.com/docs/marketing-api/reference/ad-account/assigned_users/"""
        res = set()
        me = User(fbid="me", api=self._api.api)
        accounts = [self._api.get_account(account) for account in self._account_ids]
        for business_user in me.get_business_users():
            for account in accounts:
                assigned_users = account.get_assigned_users(params={"business": business_user["business"].get_id()})
                for assigned_user in assigned_users:
                    if business_user.get_id() == assigned_user.get_id():
                        res.update(set(assigned_user["tasks"]))
        return res

    def fields(self, account_id: str, **kwargs) -> List[str]:
        if self._fields_dict.get(account_id):
            return self._fields_dict.get(account_id)

        properties = super().fields(**kwargs)
        # https://developers.facebook.com/docs/marketing-apis/guides/javascript-ads-dialog-for-payments/
        # To access "funding_source_details", the user making the API call must have a MANAGE task permission for
        # that specific ad account.
        permissions = self.get_task_permissions(account_id=account_id)
        if "funding_source_details" in properties and "MANAGE" not in permissions:
            properties.remove("funding_source_details")
        if "is_prepay_account" in properties and "MANAGE" not in permissions:
            properties.remove("is_prepay_account")

        self._fields_dict[account_id] = properties
        return properties

    def list_objects(self, account_ids_with_state: List[Tuple[str, any]]) -> Iterable:
        """noop in case of AdAccount"""
        try:
            return self._get_object_list_parallel(AdAccounts.get_account, account_ids_with_state)
        except FacebookRequestError as e:
            # This is a workaround for cases when account seem to have all the required permissions
            # but despite that is not allowed to get `owner` field. See (https://github.com/airbytehq/oncall/issues/3167)
            if e.api_error_code() == 200 and e.api_error_message() == "(#200) Requires business_management permission to manage the object":
                return self._get_object_list_parallel(AdAccounts.get_account, account_ids_with_state, ignore_fields=["owner"])

            # FB api returns a non-obvious error when accessing the `funding_source_details` field
            # even though user is granted all the required permissions (`MANAGE`)
            # https://github.com/airbytehq/oncall/issues/3031
            if e.api_error_code() == 100 and e.api_error_message() == "Unsupported request - method type: get":
                return self._get_object_list_parallel(AdAccounts.get_account, account_ids_with_state, ignore_fields=["funding_source_details"])
            raise e

    @staticmethod
    def get_account(account: FBAdAccount, account_id, fields, params):
        return [account.api_get(fields=fields, params=params)]


class Images(FBMarketingReversedIncrementalStream):
    """See: https://developers.facebook.com/docs/marketing-api/reference/ad-image"""

    def list_objects(self, account_ids_with_state: List[Tuple[str, any]]) -> Iterable:
        return self._get_object_list_parallel(api_call_wrapper=Images.get_images(), account_ids_with_state=account_ids_with_state)

    @staticmethod
    def get_images(account: FBAdAccount, account_id, fields, params):
        return [FBMarketingStream.add_account_id(record, account_id) for record in account.get_ad_images(fields=fields, params=params)]


class AdsInsightsAgeAndGender(AdsInsights):
    breakdowns = ["age", "gender"]


class AdsInsightsCountry(AdsInsights):
    breakdowns = ["country"]


class AdsInsightsRegion(AdsInsights):
    breakdowns = ["region"]


class AdsInsightsDma(AdsInsights):
    breakdowns = ["dma"]


class AdsInsightsPlatformAndDevice(AdsInsights):
    breakdowns = ["publisher_platform", "platform_position", "impression_device"]
    # FB Async Job fails for unknown reason if we set other breakdowns
    # my guess: it fails because of very large cardinality of result set (Eugene K)
    action_breakdowns = ["action_type"]


class AdsInsightsActionType(AdsInsights):
    breakdowns = []
    action_breakdowns = ["action_type"]


class AdsInsightsActionCarouselCard(AdsInsights):
    action_breakdowns = ["action_carousel_card_id", "action_carousel_card_name"]


class AdsInsightsActionConversionDevice(AdsInsights):
    breakdowns = ["device_platform"]
    action_breakdowns = ["action_type"]


class AdsInsightsActionProductID(AdsInsights):
    breakdowns = ["product_id"]
    action_breakdowns = []


class AdsInsightsActionReaction(AdsInsights):
    action_breakdowns = ["action_reaction"]


class AdsInsightsActionVideoSound(AdsInsights):
    action_breakdowns = ["action_video_sound"]


class AdsInsightsActionVideoType(AdsInsights):
    action_breakdowns = ["action_video_type"]


class AdsInsightsDeliveryDevice(AdsInsights):
    breakdowns = ["device_platform"]
    action_breakdowns = ["action_type"]


class AdsInsightsDeliveryPlatform(AdsInsights):
    breakdowns = ["publisher_platform"]
    action_breakdowns = ["action_type"]


class AdsInsightsDeliveryPlatformAndDevicePlatform(AdsInsights):
    breakdowns = ["publisher_platform", "device_platform"]
    action_breakdowns = ["action_type"]


class AdsInsightsDemographicsAge(AdsInsights):
    breakdowns = ["age"]
    action_breakdowns = ["action_type"]


class AdsInsightsDemographicsCountry(AdsInsights):
    breakdowns = ["country"]
    action_breakdowns = ["action_type"]


class AdsInsightsDemographicsDMARegion(AdsInsights):
    breakdowns = ["dma"]
    action_breakdowns = ["action_type"]


class AdsInsightsDemographicsGender(AdsInsights):
    breakdowns = ["gender"]
    action_breakdowns = ["action_type"]
