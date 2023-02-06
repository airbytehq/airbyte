#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import logging
from enum import Enum
from typing import Any, Iterator, List, Mapping, MutableMapping

import backoff
import pendulum
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.v11.services.types.google_ads_service import GoogleAdsRow, SearchGoogleAdsResponse
from google.api_core.exceptions import ServerError, TooManyRequests
from proto.marshal.collections import Repeated, RepeatedComposite

REPORT_MAPPING = {
    "accounts": "customer",
    "service_accounts": "customer",
    "ad_group_ads": "ad_group_ad",
    "ad_group_ad_labels": "ad_group_ad_label",
    "ad_groups": "ad_group",
    "ad_group_labels": "ad_group_label",
    "campaigns": "campaign",
    "campaign_labels": "campaign_label",
    "account_performance_report": "customer",
    "ad_group_ad_report": "ad_group_ad",
    "display_keyword_performance_report": "display_keyword_view",
    "display_topics_performance_report": "topic_view",
    "shopping_performance_report": "shopping_performance_view",
    "user_location_report": "user_location_view",
    "click_view": "click_view",
    "geographic_report": "geographic_view",
    "keyword_report": "keyword_view",
}
API_VERSION = "v11"
logger = logging.getLogger("airbyte")


class GoogleAds:
    DEFAULT_PAGE_SIZE = 1000

    def __init__(self, credentials: MutableMapping[str, Any]):
        # `google-ads` library version `14.0.0` and higher requires an additional required parameter `use_proto_plus`.
        # More details can be found here: https://developers.google.com/google-ads/api/docs/client-libs/python/protobuf-messages
        credentials["use_proto_plus"] = True
        self.client = GoogleAdsClient.load_from_dict(credentials, version=API_VERSION)
        self.ga_service = self.client.get_service("GoogleAdsService")

    @backoff.on_exception(
        backoff.expo,
        (ServerError, TooManyRequests),
        on_backoff=lambda details: logger.info(
            f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} seconds then retrying..."
        ),
        max_tries=5,
    )
    def send_request(self, query: str, customer_id: str) -> Iterator[SearchGoogleAdsResponse]:
        client = self.client
        search_request = client.get_type("SearchGoogleAdsRequest")
        search_request.query = query
        search_request.page_size = self.DEFAULT_PAGE_SIZE
        search_request.customer_id = customer_id
        return [self.ga_service.search(search_request)]

    def get_fields_metadata(self, fields: List[str]) -> Mapping[str, Any]:
        """
        Issue Google API request to get detailed information on data type for custom query columns.
        :params fields list of columns for user defined query.
        :return dict of fields type info.
        """

        ga_field_service = self.client.get_service("GoogleAdsFieldService")
        request = self.client.get_type("SearchGoogleAdsFieldsRequest")
        request.page_size = len(fields)
        fields_sql = ",".join([f"'{field}'" for field in fields])
        request.query = f"""
        SELECT
          name,
          data_type,
          enum_values,
          is_repeated
        WHERE name in ({fields_sql})
        """
        response = ga_field_service.search_google_ads_fields(request=request)
        return {r.name: r for r in response}

    @staticmethod
    def get_fields_from_schema(schema: Mapping[str, Any]) -> List[str]:
        properties = schema.get("properties")
        return list(properties.keys())

    @staticmethod
    def convert_schema_into_query(
        schema: Mapping[str, Any], report_name: str, from_date: str = None, to_date: str = None, cursor_field: str = None
    ) -> str:
        from_category = REPORT_MAPPING[report_name]
        fields = GoogleAds.get_fields_from_schema(schema)
        fields = ",\n".join(fields)

        query_template = f"SELECT {fields} FROM {from_category} "

        if cursor_field:
            end_date_inclusive = "<=" if (pendulum.parse(to_date) - pendulum.parse(from_date)).days > 1 else "<"
            query_template += (
                f"WHERE {cursor_field} >= '{from_date}' AND {cursor_field} {end_date_inclusive} '{to_date}' ORDER BY {cursor_field} ASC"
            )

        return query_template

    @staticmethod
    def get_field_value(field_value: GoogleAdsRow, field: str, schema_type: Mapping[str, Any]) -> str:
        field_name = field.split(".")
        for level_attr in field_name:
            """
            We have an object of the GoogleAdsRow class, and in order to get all the attributes we requested,
            we should alternately go through the nestings according to the path that we have in the field_name variable.

            For example 'field_value' looks like:
            customer {
              resource_name: "customers/4186739445"
              ...
            }
            campaign {
              resource_name: "customers/4186739445/campaigns/8765465473658"
              ....
            }
            ad_group {
              resource_name: "customers/4186739445/adGroups/2345266867978"
              ....
            }
            metrics {
              clicks: 0
              ...
            }
            ad_group_ad {
              resource_name: "customers/4186739445/adGroupAds/2345266867978~46437453679869"
              status: ENABLED
              ad {
                type_: RESPONSIVE_SEARCH_AD
                id: 46437453679869
                ....
              }
              policy_summary {
                approval_status: APPROVED
              }
            }
            segments {
              ad_network_type: SEARCH_PARTNERS
              ...
            }
            """

            try:
                field_value = getattr(field_value, level_attr)
            except AttributeError:
                # In GoogleAdsRow there are attributes that add an underscore at the end in their name.
                # For example, 'ad_group_ad.ad.type' is replaced by 'ad_group_ad.ad.type_'.
                field_value = getattr(field_value, level_attr + "_", None)
            if isinstance(field_value, Enum):
                field_value = field_value.name
            elif isinstance(field_value, (Repeated, RepeatedComposite)):
                field_value = [str(value) for value in field_value]

        # Google Ads has a lot of entities inside itself and we cannot process them all separately, because:
        # 1. It will take a long time
        # 2. We have no way to get data on absolutely all entities to test.
        #
        # To prevent JSON from throwing an error during deserialization, we made such a hack.
        # For example:
        # 1. ad_group_ad.ad.responsive_display_ad.long_headline - type AdTextAsset (https://developers.google.com/google-ads/api/reference/rpc/v6/AdTextAsset?hl=en).
        # 2. ad_group_ad.ad.legacy_app_install_ad - type LegacyAppInstallAdInfo (https://developers.google.com/google-ads/api/reference/rpc/v7/LegacyAppInstallAdInfo?hl=en).
        #
        if not (isinstance(field_value, (list, int, float, str, bool, dict)) or field_value is None):
            field_value = str(field_value)
        # In case of custom query field has MESSAGE type it represents protobuf
        # message and could be anything, convert it to a string or array of
        # string if it has "repeated" flag on metadata
        if schema_type.get("protobuf_message"):
            if "array" in schema_type.get("type"):
                field_value = [str(field) for field in field_value]
            else:
                field_value = str(field_value)

        return field_value

    @staticmethod
    def parse_single_result(schema: Mapping[str, Any], result: GoogleAdsRow):
        props = schema.get("properties")
        fields = GoogleAds.get_fields_from_schema(schema)
        single_record = {field: GoogleAds.get_field_value(result, field, props.get(field)) for field in fields}
        return single_record
