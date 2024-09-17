#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from enum import Enum
from typing import Any, Iterable, Iterator, List, Mapping, MutableMapping

import backoff
from airbyte_cdk.models import FailureType
from airbyte_cdk.utils import AirbyteTracedException
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.v17.services.types.google_ads_service import GoogleAdsRow, SearchGoogleAdsResponse
from google.api_core.exceptions import InternalServerError, ServerError, TooManyRequests
from google.auth import exceptions
from proto.marshal.collections import Repeated, RepeatedComposite

from .utils import logger

API_VERSION = "v17"


def on_give_up(details):
    error = details["exception"]
    if isinstance(error, InternalServerError):
        raise AirbyteTracedException(
            failure_type=FailureType.transient_error,
            message=f"{error.message} {error.details}",
            internal_message=f"{error.message} Unable to fetch data from Google Ads API due to temporal error on the Google Ads server. Please retry again later. ",
        )


class GoogleAds:
    DEFAULT_PAGE_SIZE = 1000

    def __init__(self, credentials: MutableMapping[str, Any]):
        # `google-ads` library version `14.0.0` and higher requires an additional required parameter `use_proto_plus`.
        # More details can be found here: https://developers.google.com/google-ads/api/docs/client-libs/python/protobuf-messages
        credentials["use_proto_plus"] = True
        self.clients = {}
        self.ga_services = {}
        self.credentials = credentials

        self.clients["default"] = self.get_google_ads_client(credentials)
        self.ga_services["default"] = self.clients["default"].get_service("GoogleAdsService")

        self.customer_service = self.clients["default"].get_service("CustomerService")

    def get_client(self, login_customer_id="default"):
        if login_customer_id in self.clients:
            return self.clients[login_customer_id]
        new_creds = self.credentials.copy()
        new_creds["login_customer_id"] = login_customer_id
        self.clients[login_customer_id] = self.get_google_ads_client(new_creds)
        return self.clients[login_customer_id]

    def ga_service(self, login_customer_id="default"):
        if login_customer_id in self.ga_services:
            return self.ga_services[login_customer_id]
        self.ga_services[login_customer_id] = self.clients[login_customer_id].get_service("GoogleAdsService")
        return self.ga_services[login_customer_id]

    @staticmethod
    def get_google_ads_client(credentials) -> GoogleAdsClient:
        try:
            return GoogleAdsClient.load_from_dict(credentials, version=API_VERSION)
        except exceptions.RefreshError as e:
            message = "The authentication to Google Ads has expired. Re-authenticate to restore access to Google Ads."
            raise AirbyteTracedException(message=message, failure_type=FailureType.config_error) from e

    def get_accessible_accounts(self):
        customer_resource_names = self.customer_service.list_accessible_customers().resource_names
        logger.info(f"Found {len(customer_resource_names)} accessible accounts: {customer_resource_names}")

        for customer_resource_name in customer_resource_names:
            customer_id = self.ga_service().parse_customer_path(customer_resource_name)["customer_id"]
            yield customer_id

    @backoff.on_exception(
        backoff.expo,
        (InternalServerError, ServerError, TooManyRequests),
        on_backoff=lambda details: logger.info(
            f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} seconds then retrying..."
        ),
        on_giveup=on_give_up,
        max_tries=5,
    )
    def send_request(
        self,
        query: str,
        customer_id: str,
        login_customer_id: str = "default",
    ) -> Iterator[SearchGoogleAdsResponse]:
        client = self.get_client(login_customer_id)
        search_request = client.get_type("SearchGoogleAdsRequest")
        search_request.query = query
        search_request.customer_id = customer_id
        return [self.ga_service(login_customer_id).search(search_request)]

    def get_fields_metadata(self, fields: List[str]) -> Mapping[str, Any]:
        """
        Issue Google API request to get detailed information on data type for custom query columns.
        :params fields list of columns for user defined query.
        :return dict of fields type info.
        """

        ga_field_service = self.get_client().get_service("GoogleAdsFieldService")
        request = self.get_client().get_type("SearchGoogleAdsFieldsRequest")
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
        fields: Iterable[str],
        table_name: str,
        conditions: List[str] = None,
        order_field: str = None,
        limit: int = None,
    ) -> str:
        """
        Constructs a Google Ads query based on the provided parameters.

        Args:
        - fields (Iterable[str]): List of fields to be selected in the query.
        - table_name (str): Name of the table from which data will be selected.
        - conditions (List[str], optional): List of conditions to be applied in the WHERE clause. Defaults to None.
        - order_field (str, optional): Field by which the results should be ordered. Defaults to None.
        - limit (int, optional): Maximum number of results to be returned. Defaults to None.

        Returns:
        - str: Constructed Google Ads query.
        """

        query_template = f"SELECT {', '.join(fields)} FROM {table_name}"

        if conditions:
            query_template += " WHERE " + " AND ".join(conditions)

        if order_field:
            query_template += f" ORDER BY {order_field} ASC"

        if limit:
            query_template += f" LIMIT {limit}"

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

        # Google Ads has a lot of entities inside itself, and we cannot process them all separately, because:
        # 1. It will take a long time
        # 2. We have no way to get data on absolutely all entities to test.
        #
        # To prevent JSON from throwing an error during deserialization, we made such a hack.
        # For example:
        # 1. ad_group_ad.ad.responsive_display_ad.long_headline - type AdTextAsset
        # (https://developers.google.com/google-ads/api/reference/rpc/v6/AdTextAsset?hl=en).
        # 2. ad_group_ad.ad.legacy_app_install_ad - type LegacyAppInstallAdInfo
        # (https://developers.google.com/google-ads/api/reference/rpc/v7/LegacyAppInstallAdInfo?hl=en).
        if not isinstance(field_value, (list, int, float, str, bool, dict)) and field_value is not None:
            field_value = str(field_value)

        return field_value

    @staticmethod
    def parse_single_result(schema: Mapping[str, Any], result: GoogleAdsRow):
        props = schema.get("properties")
        fields = GoogleAds.get_fields_from_schema(schema)
        single_record = {field: GoogleAds.get_field_value(result, field, props.get(field)) for field in fields}
        return single_record
