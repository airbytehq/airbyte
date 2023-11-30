#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Generator, Iterable, MutableMapping, Optional, Tuple, Type, Union

import pendulum
from airbyte_cdk.models import FailureType
from airbyte_cdk.utils import AirbyteTracedException
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v13.errors.types.authentication_error import AuthenticationErrorEnum
from google.ads.googleads.v13.errors.types.authorization_error import AuthorizationErrorEnum
from google.ads.googleads.v13.errors.types.quota_error import QuotaErrorEnum
from google.ads.googleads.v13.errors.types.request_error import RequestErrorEnum
from source_google_ads.google_ads import logger


def get_resource_name(stream_name: str) -> str:
    """Returns resource name for stream name"""
    return REPORT_MAPPING[stream_name] if stream_name in REPORT_MAPPING else stream_name


# maps stream name to name of resource in Google Ads
REPORT_MAPPING = {
    "account_performance_report": "customer",
    "ad_group_ad_legacy": "ad_group_ad",
    "ad_group_bidding_strategy": "ad_group",
    "ad_listing_group_criterion": "ad_group_criterion",
    "campaign_real_time_bidding_settings": "campaign",
    "campaign_bidding_strategy": "campaign",
    "service_accounts": "customer",
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
    messages = []
    raise_exception = AirbyteTracedException
    failure_type = FailureType.config_error

    for error in ga_exception.failure.errors:
        # Get error codes
        authorization_error = error.error_code.authorization_error
        authentication_error = error.error_code.authentication_error
        query_error = error.error_code.query_error
        quota_error = error.error_code.quota_error
        request_error = error.error_code.request_error

        if is_error_type(authorization_error, AuthorizationErrorEnum.AuthorizationError.USER_PERMISSION_DENIED) or is_error_type(
            authentication_error, AuthenticationErrorEnum.AuthenticationError.CUSTOMER_NOT_FOUND
        ):
            message = (
                f"Failed to access the customer '{customer_id}'. "
                f"Ensure the customer is linked to your manager account or check your permissions to access this customer account."
            )

        # If the error is encountered in the internally used class `ServiceAccounts`, an exception is raised.
        # For other classes, the error is logged and skipped to prevent sync failure. See: https://github.com/airbytehq/airbyte/issues/12486
        elif is_error_type(authorization_error, AuthorizationErrorEnum.AuthorizationError.CUSTOMER_NOT_ENABLED):
            if catch_disabled_customer_error:
                logger.error(error.message)
                continue
            else:
                message = (
                    f"The customer account '{customer_id}' hasn't finished signup or has been deactivated. "
                    "Sign in to the Google Ads UI to verify its status. "
                    "For reactivating deactivated accounts, refer to: "
                    "https://support.google.com/google-ads/answer/2375392."
                )

        elif query_error:
            message = f"Incorrect custom query. {error.message}"

        elif is_error_type(quota_error, QuotaErrorEnum.QuotaError.RESOURCE_EXHAUSTED):
            message = (
                f"The operation limits for your Google Ads account '{customer_id}' have been exceeded for the last 24 hours. "
                f"To avoid these limitations, consider applying for Standard access which offers unlimited operations per day. "
                f"Learn more about access levels and how to apply for Standard access here: "
                f"https://developers.google.com/google-ads/api/docs/access-levels#access_levels_2"
            )

        # This error occurs when the page token expires while processing results, it is partially handled in IncrementalGoogleAdsStream
        elif is_error_type(request_error, RequestErrorEnum.RequestError.EXPIRED_PAGE_TOKEN):
            message = (
                "Page token has expired during processing response. "
                "Please contact the Airbyte team with the link of your connection for assistance."
            )

            # Raise new error for easier catch in child class - this error will be handled in IncrementalGoogleAdsStream
            raise_exception = ExpiredPageTokenError
            failure_type = FailureType.system_error

        else:
            message = str(error.message)
            failure_type = FailureType.system_error

        if message:
            messages.append(message)

    if messages:
        message = "\n".join(messages)
        raise raise_exception.from_exception(failure_type=failure_type, exc=ga_exception, message=message) from ga_exception


def generator_backoff(
    wait_gen: Callable,
    exception: Union[Type[Exception], tuple],
    max_tries: Optional[int] = None,
    max_time: Optional[float] = None,
    on_backoff: Optional[Callable] = None,
    **wait_gen_kwargs: Any,
):
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Generator:
            tries = 0
            start_time = datetime.now()
            wait_times = wait_gen(**wait_gen_kwargs)
            next(wait_times)  # Skip the first yield which is None

            while True:
                try:
                    yield from func(*args, **kwargs)
                    return  # If the generator completes without error, return
                except exception as e:
                    tries += 1
                    elapsed_time = (datetime.now() - start_time).total_seconds()

                    if max_time is not None and elapsed_time >= max_time:
                        print(f"Maximum time of {max_time} seconds exceeded.")
                        raise

                    if max_tries is not None and tries >= max_tries:
                        print(f"Maximum tries of {max_tries} exceeded.")
                        raise

                    # Get the next wait time from the exponential decay generator
                    sleep_time = next(wait_times)

                    # Adjust sleep time if it exceeds the remaining max_time
                    if max_time is not None:
                        time_remaining = max_time - elapsed_time
                        sleep_time = min(sleep_time, time_remaining)

                    if on_backoff:
                        on_backoff(
                            {
                                "target": func,
                                "args": args,
                                "kwargs": kwargs,
                                "tries": tries,
                                "elapsed": elapsed_time,
                                "wait": sleep_time,
                                "exception": e,
                            }
                        )

                    time.sleep(sleep_time)

        return wrapper

    return decorator


def parse_dates(stream_slice):
    start_date = pendulum.parse(stream_slice["start_date"])
    end_date = pendulum.parse(stream_slice["end_date"])
    return start_date, end_date


def chunk_date_range(
    start_date: str,
    end_date: str = None,
    conversion_window: int = 0,
    days_of_data_storage: int = None,
    time_zone=None,
    time_format="YYYY-MM-DD",
    slice_duration: pendulum.Duration = pendulum.duration(days=14),
    slice_step: pendulum.Duration = pendulum.duration(days=1),
) -> Iterable[Optional[MutableMapping[str, any]]]:
    """
    Splits a date range into smaller chunks based on the provided parameters.

    Args:
        start_date (str): The beginning date of the range.
        end_date (str, optional): The ending date of the range. Defaults to today's date.
        conversion_window (int): Number of days to subtract from the start date. Defaults to 0.
        days_of_data_storage (int, optional): Maximum age of data that can be retrieved. Used to adjust the start date.
        time_zone: Time zone to be used for date parsing and today's date calculation. If not provided, the default time zone is used.
        time_format (str): Format to be used when returning dates. Defaults to 'YYYY-MM-DD'.
        slice_duration (pendulum.Duration): Duration of each chunk. Defaults to 14 days.
        slice_step (pendulum.Duration): Step size to move to the next chunk. Defaults to 1 day.

    Returns:
        Iterable[Optional[MutableMapping[str, any]]]: An iterable of dictionaries containing start and end dates for each chunk.
        If the adjusted start date is greater than the end date, returns a list with a None value.

    Notes:
        - If the difference between `end_date` and `start_date` is large (e.g., >= 1 month), processing all records might take a long time.
        - Tokens for fetching subsequent pages of data might expire after 2 hours, leading to potential errors.
        - The function adjusts the start date based on `days_of_data_storage` and `conversion_window` to adhere to certain data retrieval policies, such as Google Ads' policy of only retrieving data not older than a certain number of days.
        - The method returns `start_date` and `end_date` with a difference typically spanning 15 days to avoid token expiration issues.
    """
    start_date = pendulum.parse(start_date, tz=time_zone)
    today = pendulum.today(tz=time_zone)
    end_date = pendulum.parse(end_date, tz=time_zone) if end_date else today

    # For some metrics we can only get data not older than N days, it is Google Ads policy
    if days_of_data_storage:
        start_date = max(start_date, pendulum.now(tz=time_zone).subtract(days=days_of_data_storage - conversion_window))

    # As in to return some state when state in abnormal
    if start_date > end_date:
        return [None]

    # applying conversion window
    start_date = start_date.subtract(days=conversion_window)
    slice_start = start_date

    while slice_start <= end_date:
        slice_end = min(end_date, slice_start + slice_duration)
        yield {
            "start_date": slice_start.format(time_format),
            "end_date": slice_end.format(time_format),
        }
        slice_start = slice_end + slice_step


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
