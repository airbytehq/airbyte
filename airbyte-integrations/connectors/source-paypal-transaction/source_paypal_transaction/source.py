#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import base64
import json
import logging
import time
from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator, Oauth2Authenticator
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from dateutil.parser import isoparse

from .utils import middle_date_slices


class PaypalHttpException(Exception):
    """HTTPError Exception with detailed info"""

    def __init__(self, error: requests.exceptions.HTTPError):
        self.error = error

    def __str__(self):
        message = repr(self.error)

        if self.error.response.content:
            details = self.error_message()
            message = f"{message} Details: {details}"

        return message

    def error_message(self):
        content = self.error.response.content.decode()
        try:
            details = json.loads(content)
        except json.decoder.JSONDecodeError:
            details = content

        return details

    def __repr__(self):
        return self.__str__()


def get_endpoint(is_sandbox: bool = False) -> str:
    if is_sandbox:
        return "https://api-m.sandbox.paypal.com"

    return "https://api-m.paypal.com"


class PaypalTransactionStream(HttpStream, ABC):
    """Abstract class for Paypal Transaction Stream.

    Important note about 'start_date' params:
    'start_date' is one of required params, it comes from spec configuration or from stream state.
    In both cases it must meet the following conditions:

        minimum_allowed_start_date <= start_date <= end_date <= last_refreshed_datetime <= now()

    otherwise API throws an "Data for the given start date is not available" error.

    So the prevent this error 'start_date' will be reset to:
        minimum_allowed_start_date                               - if 'start_date' is too old
        min(maximum_allowed_start_date, last_refreshed_datetime) - if 'start_date' is too recent
    """

    page_size = "500"  # API limit

    # Date limits are needed to prevent API error: "Data for the given start date is not available"
    # API limit: (now() - start_date_min) <= start_date <= end_date <= last_refreshed_datetime <= now
    start_date_min: Mapping[str, int] = {"days": 3 * 365}  # API limit - 3 years
    last_refreshed_datetime: Optional[datetime] = None  # extracted from API response. Indicate the most resent possible start_date
    stream_slice_period: Mapping[str, int] = {"days": 15}  # max period is 31 days (API limit)

    requests_per_minute: int = 30  # API limit is 50 reqs/min from 1 IP to all endpoints, otherwise IP is banned for 5 mins
    # if the stream has nested cursor_field, we should trry to unnest it once parsing the recods to avoid normalization conflicts.
    unnest_cursor: bool = False
    unnest_pk: bool = False
    nested_object: str = None

    def __init__(
        self,
        authenticator: HttpAuthenticator,
        start_date: Union[datetime, str],
        end_date: Union[datetime, str] = None,
        is_sandbox: bool = False,
        **kwargs,
    ):
        now = datetime.now().replace(microsecond=0).astimezone()

        if end_date and isinstance(end_date, str):
            end_date = isoparse(end_date)
        self.end_date: datetime = end_date if end_date and end_date < now else now

        if start_date and isinstance(start_date, str):
            start_date = isoparse(start_date)

        minimum_allowed_start_date = now - timedelta(**self.start_date_min)
        if start_date < minimum_allowed_start_date:
            self.logger.log(
                logging.WARN,
                f'Stream {self.name}: start_date "{start_date.isoformat()}" is too old. '
                + f'Reset start_date to the minimum_allowed_start_date "{minimum_allowed_start_date.isoformat()}"',
            )
            start_date = minimum_allowed_start_date

        self.maximum_allowed_start_date = min(now, self.end_date)
        if start_date > self.maximum_allowed_start_date:
            self.logger.log(
                logging.WARN,
                f'Stream {self.name}: start_date "{start_date.isoformat()}" is too recent. '
                + f'Reset start_date to the maximum_allowed_start_date "{self.maximum_allowed_start_date.isoformat()}"',
            )
            start_date = self.maximum_allowed_start_date

        self.start_date = start_date

        self.is_sandbox = is_sandbox

        super().__init__(authenticator=authenticator)

    def validate_input_dates(self):
        # Validate input dates
        if self.start_date > self.end_date:
            raise Exception(f"start_date {self.start_date.isoformat()} is greater than end_date {self.end_date.isoformat()}")

    @property
    def url_base(self) -> str:
        return f"{get_endpoint(self.is_sandbox)}/v1/reporting/"

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Content-Type": "application/json"}

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        # API limit is 50 reqs/min from 1 IP to all endpoints, otherwise IP is banned for 5 mins
        return 5 * 60.1

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()

        # Save extracted last_refreshed_datetime to use it as maximum allowed start_date
        last_refreshed_datetime = json_response.get("last_refreshed_datetime")
        self.last_refreshed_datetime = isoparse(last_refreshed_datetime) if last_refreshed_datetime else None

        if self.data_field is not None:
            data = json_response.get(self.data_field, [])
        else:
            data = [json_response]

        for record in data:
            # In order to support direct datetime string comparison (which is performed in incremental acceptance tests)
            # convert any date format to python iso format string for date based cursors
            self.update_field(record, self.cursor_field, lambda date: isoparse(date).isoformat())
            # unnest cursor_field to handle normalization correctly
            if self.unnest_cursor:
                self.unnest_field(record, self.nested_object, self.cursor_field)
            # unnest primary_key to handle normalization correctly
            if self.unnest_pk:
                self.unnest_field(record, self.nested_object, self.primary_key)
            yield record

        # sleep for 1-2 secs to not reach rate limit: 50 requests per minute
        time.sleep(60 / self.requests_per_minute)

    @staticmethod
    def unnest_field(record: Mapping[str, Any], unnest_from: Dict, cursor_field: str):
        """
        Unnest cursor_field to the root level of the record.
        """
        if unnest_from in record:
            record[cursor_field] = record.get(unnest_from).get(cursor_field)

    @staticmethod
    def update_field(record: Mapping[str, Any], field_path: Union[List[str], str], update: Callable[[Any], None]):
        if not isinstance(field_path, List):
            field_path = [field_path]

        last_field = field_path[-1]
        data = PaypalTransactionStream.get_field(record, field_path[:-1])
        if data and last_field in data:
            data[last_field] = update(data[last_field])

    @staticmethod
    def get_field(record: Mapping[str, Any], field_path: Union[List[str], str]):

        if not isinstance(field_path, List):
            field_path = [field_path]

        data = record
        for attr in field_path:
            if data and isinstance(data, dict):
                data = data.get(attr)
            else:
                return None

        return data

    @staticmethod
    def max_records_in_response_reached(exception: Exception, **kwargs):
        message = exception.error_message()
        return message.get("name") == "RESULTSET_TOO_LARGE"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, any]:
        # This method is called once for each record returned from the API to compare the cursor field value in that record with the current state
        # we then return an updated state object. If this is the first time we run a sync or no state was passed, current_stream_state will be None.
        latest_record_date_str: str = self.get_field(latest_record, self.cursor_field)

        if current_stream_state and "date" in current_stream_state and latest_record_date_str:
            # isoparse supports different formats, like:
            # python iso format:               2021-06-04T00:00:00+03:00
            # format from transactions record: 2021-06-04T00:00:00+0300
            # format from balances record:     2021-06-02T00:00:00Z
            latest_record_date = isoparse(latest_record_date_str)
            current_parsed_date = isoparse(current_stream_state["date"])

            return {"date": max(current_parsed_date, latest_record_date).isoformat()}
        else:
            return {"date": self.start_date.isoformat()}

    def get_last_refreshed_datetime(self, sync_mode):
        """Get last_refreshed_datetime attribute from API response by running PaypalTransactionStream().read_records()
        with 'empty' stream_slice (range=0)

        last_refreshed_datetime indicates the maximum available start_date for which API has data.
        If request start_date > last_refreshed_datetime then API throws an error:
            "Data for the given start date is not available"
        """
        paypal_stream = self.__class__(
            authenticator=self.authenticator,
            start_date=self.start_date,
            end_date=self.start_date,
            is_sandbox=self.is_sandbox,
        )
        stream_slice = {
            "start_date": self.start_date.isoformat(),
            "end_date": self.start_date.isoformat(),
        }
        list(paypal_stream.read_records(sync_mode=sync_mode, stream_slice=stream_slice))
        return paypal_stream.last_refreshed_datetime

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, any]]]:
        """
        Returns a list of slices for each day (by default) between the start date and end date.
        The return value is a list of dicts {'start_date': date_string, 'end_date': date_string}.
        """
        period = timedelta(**self.stream_slice_period)

        # get last_refreshed_datetime from API response to use as maximum allowed start_date
        self.last_refreshed_datetime = self.get_last_refreshed_datetime(sync_mode)
        if self.last_refreshed_datetime:
            self.logger.info(f"Maximum allowed start_date is {self.last_refreshed_datetime} based on info from API response")
            self.maximum_allowed_start_date = min(self.last_refreshed_datetime, self.maximum_allowed_start_date)

        slice_start_date = self.start_date

        if stream_state:
            # if stream_state_date is in the future (for example during tests) then reset it to maximum_allowed_start_date:
            stream_state_date = min(isoparse(stream_state.get("date")), self.maximum_allowed_start_date)

            # slice_start_date should be the most recent date:
            slice_start_date = max(slice_start_date, stream_state_date)

        slices = []
        while slice_start_date <= self.maximum_allowed_start_date:
            slices.append(
                {
                    "start_date": slice_start_date.isoformat(),
                    "end_date": min(slice_start_date + period, self.end_date).isoformat(),
                }
            )
            slice_start_date += period

        return slices

    def _prepared_request(
        self, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None, next_page_token: Optional[dict] = None
    ):
        request_headers = self.request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        request = self._create_prepared_request(
            path=self.path(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            headers=dict(request_headers, **self.authenticator.get_auth_header()),
            params=self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            json=self.request_body_json(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            data=self.request_body_data(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
        )
        request_kwargs = self.request_kwargs(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

        return request, request_kwargs

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        pagination_complete = False
        next_page_token = None
        while not pagination_complete:
            request, request_kwargs = self._prepared_request(
                stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
            )

            try:
                response = self._send_request(request, request_kwargs)
            except PaypalHttpException as exception:
                if self.max_records_in_response_reached(exception):
                    date_slices = middle_date_slices(stream_slice)
                    if date_slices:
                        for date_slice in date_slices:
                            yield from self.read_records(
                                sync_mode, cursor_field=cursor_field, stream_slice=date_slice, stream_state=stream_state
                            )
                        break
                    else:
                        raise exception

            yield from self.parse_response(response, stream_state=stream_state, stream_slice=stream_slice)

            next_page_token = self.next_page_token(response)
            if not next_page_token:
                pagination_complete = True

        # Always return an empty generator just in case no records were ever yielded
        yield from []

    def _send_request(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:
        try:
            return super()._send_request(request, request_kwargs)
        except requests.exceptions.HTTPError as http_error:
            raise PaypalHttpException(http_error)


class Transactions(PaypalTransactionStream):
    """List Paypal Transactions on a specific date range
    API Docs: https://developer.paypal.com/docs/integration/direct/transaction-search/#list-transactions
    Endpoint: /v1/reporting/transactions
    """

    data_field = "transaction_details"
    nested_object = "transaction_info"

    primary_key = "transaction_id"
    cursor_field = "transaction_initiation_date"

    unnest_cursor = True
    unnest_pk = True

    transformer = TypeTransformer(TransformConfig.CustomSchemaNormalization)

    # TODO handle API error when 1 request returns more than 10000 records.
    # https://github.com/airbytehq/airbyte/issues/4404
    records_per_request = 10000

    def path(self, **kwargs) -> str:
        return "transactions"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        total_pages = decoded_response.get("total_pages")
        page_number = decoded_response.get("page")
        if page_number < total_pages:
            return {"page": page_number + 1}
        else:
            return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        page_number = 1
        if next_page_token:
            page_number = next_page_token.get("page")

        return {
            "start_date": stream_slice["start_date"],
            "end_date": stream_slice["end_date"],
            "fields": "all",
            "page_size": self.page_size,
            "page": page_number,
        }

    @transformer.registerCustomTransform
    def transform_function(original_value: Any, field_schema: Dict[str, Any]) -> Any:
        if isinstance(original_value, str) and field_schema["type"] == "number":
            return float(original_value)
        elif isinstance(original_value, str) and field_schema["type"] == "integer":
            return int(original_value)
        else:
            return original_value


class Balances(PaypalTransactionStream):
    """Get account balance on a specific date
    API Docs: https://developer.paypal.com/docs/integration/direct/transaction-search/#check-balancess
    """

    primary_key = "as_of_time"
    cursor_field = "as_of_time"
    data_field = None

    def path(self, **kwargs) -> str:
        return "balances"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            "as_of_time": stream_slice["start_date"],
        }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None


class PayPalOauth2Authenticator(Oauth2Authenticator):
    """Request example for API token extraction:
    For `old_config` scenario:
        curl -v POST https://api-m.sandbox.paypal.com/v1/oauth2/token \
        -H "Accept: application/json" \
        -H "Accept-Language: en_US" \
        -u "CLIENT_ID:SECRET" \
        -d "grant_type=client_credentials"
    """

    def __init__(self, config: Dict):
        self.old_config: bool = False
        # default auth args
        self.auth_args: Dict = {
            "token_refresh_endpoint": f"{get_endpoint(config['is_sandbox'])}/v1/oauth2/token",
            "refresh_token": "",
        }
        # support old configs
        if "client_id" and "secret" in config:
            self.old_config = True
            self.auth_args.update(
                **{"client_id": config["client_id"], "client_secret": config["secret"], "refresh_token": config.get("refresh_token")}
            )
        # new configs
        if "credentials" in config:
            credentials = config.get("credentials")
            auth_type = credentials.get("auth_type")
            self.auth_args.update(**{"client_id": credentials["client_id"], "client_secret": credentials["client_secret"]})
            if auth_type == "oauth2.0":
                self.auth_args["refresh_token"] = credentials["refresh_token"]
            elif auth_type == "private_oauth":
                self.old_config = True

        self.config = config
        super().__init__(**self.auth_args)

    def get_headers(self):
        # support old configs
        if self.old_config:
            return {"Accept": "application/json", "Accept-Language": "en_US"}
        # new configs
        basic_auth = base64.b64encode(bytes(f"{self.client_id}:{self.client_secret}", "utf-8")).decode("utf-8")
        return {"Authorization": f"Basic {basic_auth}"}

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        # support old configs
        if self.old_config:
            return {"grant_type": "client_credentials"}
        # new configs
        return {"grant_type": "refresh_token", "refresh_token": self.refresh_token}

    def refresh_access_token(self) -> Tuple[str, int]:
        """
        returns a tuple of (access_token, token_lifespan_in_seconds)
        """
        request_args = {
            "url": self.token_refresh_endpoint,
            "data": self.get_refresh_request_body(),
            "headers": self.get_headers(),
        }
        try:
            # support old configs
            if self.old_config:
                request_args["auth"] = (self.client_id, self.client_secret)
            response = requests.post(**request_args)
            response.raise_for_status()
            response_json = response.json()
            return response_json["access_token"], response_json["expires_in"]
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e


class SourcePaypalTransaction(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        authenticator = PayPalOauth2Authenticator(config)

        # Try to get API TOKEN
        token = authenticator.get_access_token()
        if not token:
            return False, "Unable to fetch Paypal API token due to incorrect client_id or secret"

        # Try to initiate a stream and validate input date params
        try:
            # validate input date ranges
            Transactions(authenticator=authenticator, **config).validate_input_dates()

            # validate if Paypal API is able to extract data for given start_data
            start_date = isoparse(config["start_date"])
            end_date = start_date + timedelta(days=1)
            stream_slice = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            }
            records = Transactions(authenticator=authenticator, **config).read_records(sync_mode=None, stream_slice=stream_slice)
            # Try to read one value from records iterator
            next(records, None)
            return True, None
        except Exception as e:
            if "Data for the given start date is not available" in repr(e):
                return False, f"Data for the given start date ({config['start_date']}) is not available, please use more recent start date"
            else:
                return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        authenticator = PayPalOauth2Authenticator(config)

        return [
            Transactions(authenticator=authenticator, **config),
            Balances(authenticator=authenticator, **config),
        ]
