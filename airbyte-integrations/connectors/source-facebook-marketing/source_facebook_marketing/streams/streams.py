#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import logging
from typing import Any, Iterable, List, Mapping, Optional, Set

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from cached_property import cached_property
from facebook_business.adobjects.adaccount import AdAccount as FBAdAccount
from facebook_business.adobjects.adimage import AdImage
from facebook_business.adobjects.user import User
from facebook_business.exceptions import FacebookRequestError

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
    """AdCreative is append only stream
    doc: https://developers.facebook.com/docs/marketing-api/reference/ad-creative
    """

    entity_prefix = "adcreative"
    enable_deleted = False

    def __init__(self, fetch_thumbnail_images: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._fetch_thumbnail_images = fetch_thumbnail_images

    @cached_property
    def fields(self) -> List[str]:
        """Remove "thumbnail_data_url" field because it is computed field and it's not a field that we can request from Facebook"""
        return [f for f in super().fields if f != "thumbnail_data_url"]

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

    def list_objects(self, params: Mapping[str, Any]) -> Iterable:
        return self._api.account.get_ad_creatives(params=params, fields=self.fields)


class CustomConversions(FBMarketingStream):
    """doc: https://developers.facebook.com/docs/marketing-api/reference/custom-conversion"""

    entity_prefix = "customconversion"
    enable_deleted = False

    def list_objects(self, params: Mapping[str, Any]) -> Iterable:
        return self._api.account.get_custom_conversions(params=params, fields=self.fields)


class CustomAudiences(FBMarketingStream):
    """doc: https://developers.facebook.com/docs/marketing-api/reference/custom-audience"""

    entity_prefix = "customaudience"
    enable_deleted = False
    # The `rule` field is excluded from the list because it caused the error message "Please reduce the amount of data" for certain connections.
    # https://github.com/airbytehq/oncall/issues/2765
    fields_exceptions = ["rule"]

    def list_objects(self, params: Mapping[str, Any]) -> Iterable:
        return self._api.account.get_custom_audiences(params=params, fields=self.fields)


class Ads(FBMarketingIncrementalStream):
    """doc: https://developers.facebook.com/docs/marketing-api/reference/adgroup"""

    entity_prefix = "ad"

    def list_objects(self, params: Mapping[str, Any]) -> Iterable:
        return self._api.account.get_ads(params=params, fields=self.fields)


class AdSets(FBMarketingIncrementalStream):
    """doc: https://developers.facebook.com/docs/marketing-api/reference/ad-campaign"""

    entity_prefix = "adset"

    def list_objects(self, params: Mapping[str, Any]) -> Iterable:
        return self._api.account.get_ad_sets(params=params, fields=self.fields)


class Campaigns(FBMarketingIncrementalStream):
    """doc: https://developers.facebook.com/docs/marketing-api/reference/ad-campaign-group"""

    entity_prefix = "campaign"

    def list_objects(self, params: Mapping[str, Any]) -> Iterable:
        return self._api.account.get_campaigns(params=params, fields=self.fields)


class Activities(FBMarketingIncrementalStream):
    """doc: https://developers.facebook.com/docs/marketing-api/reference/ad-activity"""

    entity_prefix = "activity"
    cursor_field = "event_time"
    primary_key = None

    def list_objects(self, params: Mapping[str, Any]) -> Iterable:
        return self._api.account.get_activities(fields=self.fields, params=params)

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

        potentially_new_records_in_the_past = self._include_deleted and not stream_state.get("include_deleted", False)
        if potentially_new_records_in_the_past:
            self.logger.info(f"Ignoring bookmark for {self.name} because of enabled `include_deleted` option")
            if self._start_date:
                since = self._start_date
            else:
                # if start_date is not specified then do not use date filters
                return {}

        return {"since": since.int_timestamp}


class Videos(FBMarketingReversedIncrementalStream):
    """See: https://developers.facebook.com/docs/marketing-api/reference/video"""

    entity_prefix = "video"

    def list_objects(self, params: Mapping[str, Any]) -> Iterable:
        # Remove filtering as it is not working for this stream since 2023-01-13
        return self._api.account.get_ad_videos(params=params, fields=self.fields)


class AdAccount(FBMarketingStream):
    """See: https://developers.facebook.com/docs/marketing-api/reference/ad-account"""

    use_batch = False
    enable_deleted = False

    def get_task_permissions(self) -> Set[str]:
        """https://developers.facebook.com/docs/marketing-api/reference/ad-account/assigned_users/"""
        res = set()
        me = User(fbid="me", api=self._api.api)
        for business_user in me.get_business_users():
            assigned_users = self._api.account.get_assigned_users(params={"business": business_user["business"].get_id()})
            for assigned_user in assigned_users:
                if business_user.get_id() == assigned_user.get_id():
                    res.update(set(assigned_user["tasks"]))
        return res

    @cached_property
    def fields(self) -> List[str]:
        properties = super().fields
        # https://developers.facebook.com/docs/marketing-apis/guides/javascript-ads-dialog-for-payments/
        # To access "funding_source_details", the user making the API call must have a MANAGE task permission for
        # that specific ad account.
        permissions = self.get_task_permissions()
        if "funding_source_details" in properties and "MANAGE" not in permissions:
            properties.remove("funding_source_details")
        if "is_prepay_account" in properties and "MANAGE" not in permissions:
            properties.remove("is_prepay_account")
        return properties

    def list_objects(self, params: Mapping[str, Any]) -> Iterable:
        """noop in case of AdAccount"""
        fields = self.fields
        try:
            return [FBAdAccount(self._api.account.get_id()).api_get(fields=fields)]
        except FacebookRequestError as e:
            # This is a workaround for cases when account seem to have all the required permissions
            # but despite of that is not allowed to get `owner` field. See (https://github.com/airbytehq/oncall/issues/3167)
            if e.api_error_code() == 200 and e.api_error_message() == "(#200) Requires business_management permission to manage the object":
                fields.remove("owner")
                return [FBAdAccount(self._api.account.get_id()).api_get(fields=fields)]
            # FB api returns a non-obvious error when accessing the `funding_source_details` field
            # even though user is granted all the required permissions (`MANAGE`)
            # https://github.com/airbytehq/oncall/issues/3031
            if e.api_error_code() == 100 and e.api_error_message() == "Unsupported request - method type: get":
                fields.remove("funding_source_details")
                return [FBAdAccount(self._api.account.get_id()).api_get(fields=fields)]
            raise e


class Images(FBMarketingReversedIncrementalStream):
    """See: https://developers.facebook.com/docs/marketing-api/reference/ad-image"""

    def list_objects(self, params: Mapping[str, Any]) -> Iterable:
        return self._api.account.get_ad_images(params=params, fields=self.fields)

    def get_record_deleted_status(self, record) -> bool:
        return record[AdImage.Field.status] == AdImage.Status.deleted


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
