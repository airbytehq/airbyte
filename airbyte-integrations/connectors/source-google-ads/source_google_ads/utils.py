#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re
from dataclasses import dataclass
from typing import Optional, Tuple

from airbyte_cdk.models import FailureType
from airbyte_cdk.utils import AirbyteTracedException
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v13.errors.types.authentication_error import AuthenticationErrorEnum
from google.ads.googleads.v13.errors.types.authorization_error import AuthorizationErrorEnum
from google.ads.googleads.v13.errors.types.quota_error import QuotaErrorEnum
from google.ads.googleads.v13.errors.types.request_error import RequestErrorEnum
from source_google_ads.google_ads import logger

# maps stream name to name of resource in Google Ads
REPORT_MAPPING = {
    "accounts": "customer",
    "account_labels": "customer_label",
    "account_performance_report": "customer",
    "ad_group_ads": "ad_group_ad",
    "ad_group_ad_labels": "ad_group_ad_label",
    "ad_group_ad_report": "ad_group_ad",
    "ad_groups": "ad_group",
    "ad_group_bidding_strategies": "ad_group",
    "ad_group_criterions": "ad_group_criterion",
    "ad_group_criterion_labels": "ad_group_criterion_label",
    "ad_group_labels": "ad_group_label",
    "ad_listing_group_criterions": "ad_group_criterion",
    "audience": "audience",
    "campaigns": "campaign",
    "campaign_real_time_bidding_settings": "campaign",
    "campaign_criterion": "campaign_criterion",
    "campaign_bidding_strategies": "campaign",
    "campaign_budget": "campaign_budget",
    "campaign_labels": "campaign_label",
    "change_status": "change_status",
    "click_view": "click_view",
    "display_keyword_performance_report": "display_keyword_view",
    "display_topics_performance_report": "topic_view",
    "geographic_report": "geographic_view",
    "keyword_report": "keyword_view",
    "labels": "label",
    "service_accounts": "customer",
    "shopping_performance_report": "shopping_performance_view",
    "user_interest": "user_interest",
    "user_location_report": "user_location_view",
}


class ExpiredPageTokenError(AirbyteTracedException):
    """
    Custom AirbyteTracedException exception to handle the scenario when the page token has expired
    while processing a response from Google Ads.
    """

    pass


def is_error_type(error_value, target_enum_value):
    """Compares error value with target enum value after converting both to integers."""
    return int(error_value) == int(target_enum_value)


def traced_exception(ga_exception: GoogleAdsException, customer_id: str, catch_disabled_customer_error: bool):
    """Add user-friendly message for GoogleAdsException"""
    unknown_error = False
    for error in ga_exception.failure.errors:
        authorization_error = error.error_code.authorization_error
        authentication_error = error.error_code.authentication_error
        if (is_error_type(authorization_error, AuthorizationErrorEnum.AuthorizationError.USER_PERMISSION_DENIED) or
                is_error_type(authentication_error, AuthenticationErrorEnum.AuthenticationError.CUSTOMER_NOT_FOUND)):
            message = f"Failed to access the customer '{customer_id}'. Ensure the customer is linked to your manager account or check your permissions to access this customer account."
            raise AirbyteTracedException(
                message=message, failure_type=FailureType.config_error, exception=ga_exception, internal_message=message
            )

        # If the error is encountered in the internally used class `ServiceAccounts`, an exception is raised.
        # For other classes, the error is logged and skipped to prevent sync failure. See: https://github.com/airbytehq/airbyte/issues/12486
        is_customer_disabled = is_error_type(authorization_error, AuthorizationErrorEnum.AuthorizationError.CUSTOMER_NOT_ENABLED)
        if is_customer_disabled:
            if catch_disabled_customer_error:
                logger.error(error.message)
                continue
            else:
                message = (
                    f"The Google Ads account '{customer_id}' you're trying to access is not enabled. "
                    "This may occur if the account hasn't been fully set up or activated. "
                    "Please ensure that you've completed all necessary setup steps in the Google Ads platform and that the account is active. "
                    "If the account is recently created, it might take some time before it's fully activated."
                )
                raise AirbyteTracedException.from_exception(
                    ga_exception, message=message, failure_type=FailureType.config_error
                ) from ga_exception

        query_error = error.error_code.query_error
        if query_error:
            message = f"Incorrect custom query. {error.message}"
            raise AirbyteTracedException.from_exception(
                ga_exception, message=message, failure_type=FailureType.config_error
            ) from ga_exception

        quota_error = error.error_code.quota_error
        if is_error_type(quota_error, QuotaErrorEnum.QuotaError.RESOURCE_EXHAUSTED):
            message = (
                f"You've exceeded your 24-hour quota limits for operations on your Google Ads account '{customer_id}'. Try again later."
            )
            raise AirbyteTracedException.from_exception(
                ga_exception, message=message, failure_type=FailureType.config_error
            ) from ga_exception

        request_error = error.error_code.request_error
        if is_error_type(request_error, RequestErrorEnum.RequestError.EXPIRED_PAGE_TOKEN):
            message = "Page token has expired during processing response."
            # raise new error for easier catch in child class - this error will be handled in IncrementalGoogleAdsStream
            raise ExpiredPageTokenError(message=message, failure_type=FailureType.system_error, exception=ga_exception) from ga_exception

        unknown_error = True

    if unknown_error:
        message = ", ".join([error.message for error in ga_exception.failure.errors])
        raise AirbyteTracedException(
            message=message, failure_type=FailureType.system_error, exception=ga_exception, internal_message=message
        )


@dataclass(repr=False, eq=False, frozen=True)
class GAQL:
    """
    Simple regex parser of Google Ads Query Language
    https://developers.google.com/google-ads/api/docs/query/grammar
    """

    fields: Tuple[str]
    resource_name: str
    where: str
    order_by: str
    limit: Optional[int]
    parameters: str

    REGEX = re.compile(
        r"""\s*
            SELECT\s+(?P<FieldNames>\S.*)
            \s+
            FROM\s+(?P<ResourceNames>[a-z][a-zA-Z_]*(\s*,\s*[a-z][a-zA-Z_]*)*)
            \s*
            (\s+WHERE\s+(?P<WhereClause>\S.*?))?
            (\s+ORDER\s+BY\s+(?P<OrderByClause>\S.*?))?
            (\s+LIMIT\s+(?P<LimitClause>[1-9]([0-9])*))?
            \s*
            (\s+PARAMETERS\s+(?P<ParametersClause>\S.*?))?
            $""",
        flags=re.I | re.DOTALL | re.VERBOSE,
    )

    REGEX_FIELD_NAME = re.compile(r"^[a-z][a-z0-9._]*$", re.I)

    @classmethod
    def parse(cls, query):
        m = cls.REGEX.match(query)
        if not m:
            raise ValueError

        fields = [f.strip() for f in m.group("FieldNames").split(",")]
        for field in fields:
            if not cls.REGEX_FIELD_NAME.match(field):
                raise ValueError

        resource_names = re.split(r"\s*,\s*", m.group("ResourceNames"))
        if len(resource_names) > 1:
            raise ValueError
        resource_name = resource_names[0]

        where = cls._normalize(m.group("WhereClause") or "")
        order_by = cls._normalize(m.group("OrderByClause") or "")
        limit = m.group("LimitClause")
        if limit:
            limit = int(limit)
        parameters = cls._normalize(m.group("ParametersClause") or "")
        return cls(tuple(fields), resource_name, where, order_by, limit, parameters)

    def __str__(self):
        fields = ", ".join(self.fields)
        query = f"SELECT {fields} FROM {self.resource_name}"
        if self.where:
            query += " WHERE " + self.where
        if self.order_by:
            query += " ORDER BY " + self.order_by
        if self.limit is not None:
            query += " LIMIT " + str(self.limit)
        if self.parameters:
            query += " PARAMETERS " + self.parameters
        return query

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def _normalize(s):
        s = s.strip()
        return re.sub(r"\s+", " ", s)

    def set_where(self, value: str):
        return self.__class__(self.fields, self.resource_name, value, self.order_by, self.limit, self.parameters)

    def set_limit(self, value: int):
        return self.__class__(self.fields, self.resource_name, self.where, self.order_by, value, self.parameters)

    def append_field(self, value):
        fields = list(self.fields)
        fields.append(value)
        return self.__class__(tuple(fields), self.resource_name, self.where, self.order_by, self.limit, self.parameters)
