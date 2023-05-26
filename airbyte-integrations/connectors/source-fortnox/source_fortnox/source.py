#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
import backoff
import logging

import requests
import pendulum

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream, IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.requests_native_auth import SingleUseRefreshTokenOauth2Authenticator
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException

from airbyte_cdk.models import SyncMode
from datetime import datetime

from .helper import signal_last

logger = logging.getLogger('airbyte')


"""
The page size is sent to Fortnox as the request parameter limit.

Valid values are 1 to 500, defaulting to 100 if not set
"""
PAGE_SIZE = 500


class FortnoxRefreshingAuthenticator(SingleUseRefreshTokenOauth2Authenticator):

    def __init__(self, config):
        super(FortnoxRefreshingAuthenticator, self).__init__(config, "https://apps.fortnox.se/oauth-v1/token")

    def token_has_expired(self) -> bool:
        """Returns True if the token is expired

        An error happened after the sync had been running an hour, where the remote server reported that the token
        was expired when the request was actually performed.

        After checking the logs, and as far as I remember, the request was made five seconds after the token was expired. Suspect
        this may have to do with the 5 second backoff that happens quite frequently in this connector since
        there is no client-side throttling implemented. or maybe it was before cannot quite remember!

        Regardless of the root cause of this, I decided to force a refresh a minute earlier than needed just
        to be on the safe side for any issues with latency that may cause this client to assume this token
        is valid for longer than it actually is.
        """
        return pendulum.now("UTC") > self.get_token_expiry_date() - pendulum.duration(minutes=1)

    @backoff.on_exception(
        backoff.expo,
        DefaultBackoffException,
        on_backoff=lambda details: logger.info(
            f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} seconds then retrying..."
        ),
        max_time=300,
    )
    def _get_refresh_access_token_response(self):
        try:
            body = self.build_refresh_request_body()
            del body["client_id"]
            del body["client_secret"]
            response = requests.request(method="POST",
                                        url=self.get_token_refresh_endpoint(),
                                        auth=(self.get_client_id(),
                                              self.get_client_secret()),
                                        data=body)
            response.raise_for_status()
            logger.info("Refreshing access token")
            return response.json()
        except requests.exceptions.RequestException as e:
            if e.response.status_code == 429 or e.response.status_code >= 500:
                raise DefaultBackoffException(request=e.response.request, response=e.response)
            raise
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e


class FortnoxStream(HttpStream, ABC):
    """
        This is the base class for all the Fortnox streams
    """

    url_base = "https://api.fortnox.se/3/"

    @property
    @abstractmethod
    def root_element(self) -> str:
        """This is the name of the root element of the response"""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the
                response.
                If there are no more pages in the result, return None.
        """
        json_response = response.json()

        next_page = json_response.get('MetaInformation', {}).get("@CurrentPage", -1) + 1
        if next_page == 0:
            return None
        total_pages = json_response.get('MetaInformation', {}).get("@TotalPages")

        if next_page > total_pages:
            # We have reached the end
            return None

        return {'page': next_page}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            "limit": PAGE_SIZE,
            **(next_page_token if next_page_token is not None else {}),
        }

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
            Implements a backoff time of a hardcoded 5 seconds, according to the documentation a maximum amount of requests
            under a sliding window of 5 seconds is 25 requests from the same access token is allowed before the
            server responds with http status 429

            See: https://developer.fortnox.se/general/regarding-fortnox-api-rate-limits/
        """
        return float(5)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json().get(self.root_element, [])


class FortnoxIncrementalStream(FortnoxStream, IncrementalMixin, ABC):
    cursor_field = "lastmodified"  # There is no field we could read from in the payload
    _cursor_value = None
    stashed_date = None

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value}

        return {self.cursor_field: None}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value[self.cursor_field]

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        """
        Even though this get_updated_state is deprecated it is nonetheless needed when working with
        substreams, if this method doesn't return the new state the state is cleared for the next slice.
        """
        return self.state

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        request_params = super(FortnoxIncrementalStream, self).request_params(stream_state, stream_slice, next_page_token)
        if stream_state.get(self.cursor_field, None) is not None:
            request_params["lastmodified"] = stream_state[self.cursor_field]
        return request_params

    def read_records(
            self,
            sync_mode: SyncMode,
            cursor_field: List[str] = None,
            stream_slice: Mapping[str, Any] = None,
            stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        if sync_mode == SyncMode.incremental and \
                (stream_slice is None or stream_slice.get("parent", {}).get("@is_first", True)):
            self.stashed_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"Recording the time {self.cursor_field}={self.stashed_date}, to be persisted on the last slice")

        yield from super(FortnoxIncrementalStream, self).read_records(sync_mode, cursor_field, stream_slice, stream_state)

        # Only update the cursor value if the full sync was successful
        if sync_mode == SyncMode.incremental and \
                (stream_slice is None or stream_slice.get("parent", {}).get("@is_last", True)):
            logger.info(f"This was the last slice saving the cursor field {self.cursor_field}={self.stashed_date}")
            self._cursor_value = self.stashed_date


class FortnoxSubstream(HttpSubStream, ABC):

    def stream_slices(
            self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        We need to mark the first and the last slice so that the exact date can be stashed away in the incremental
        stream BEFORE we make the first request on the first slice, and then AFTER all slices have been
        successfully we update the state to the stashed away date.

        This is to make sure that there are no lost records, there doesn't exist a modified date on the records
        themselves, so one cannot commit anything before we know that the whole incremental batch is processed
        successfully.

        @see FortnoxIncrementalStream.read_records

        Theoretically it may be possible to use slicing of the stream in conjunction with last modified date, by
        using the parameters fromdate and todate these dates however refer to dates that are not set by a trigger,
        but could potentially be set by a user.
        """
        is_first = True
        for is_last, the_slice in signal_last(super(FortnoxSubstream, self).stream_slices(sync_mode, cursor_field, stream_state)):
            the_slice["parent"]["@is_last"] = is_last
            the_slice["parent"]["@is_first"] = is_first
            is_first = False
            yield the_slice


class FinancialYearParentMixin(FortnoxStream, ABC):

    use_cache = True

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        super_params = super(FinancialYearParentMixin, self).request_params(stream_state, stream_slice, next_page_token)
        financial_year = stream_slice.get("parent", {}).get("Id", None)
        if financial_year is not None:
            super_params["financialyear"] = financial_year
        return super_params


class Accounts(FortnoxIncrementalStream, FortnoxSubstream, FinancialYearParentMixin):
    primary_key = "Number"
    root_element = "Accounts"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "accounts"


class CostCenters(FortnoxIncrementalStream):
    primary_key = "Code"
    root_element = "CostCenters"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "costcenters"


class Customers(FortnoxIncrementalStream):
    primary_key = "CustomerNumber"
    root_element = "Customers"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "customers"


class FinancialYears(FortnoxStream):
    primary_key = "Id"
    root_element = "FinancialYears"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "financialyears"


class Invoices(FortnoxIncrementalStream):
    primary_key = "DocumentNumber"
    root_element = "Invoices"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "invoices"


class Projects(FortnoxIncrementalStream):
    primary_key = "ProjectNumber"
    root_element = "Projects"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "projects"


class Vouchers(FortnoxSubstream, FortnoxIncrementalStream, FinancialYearParentMixin):
    primary_key = ["Year", "VoucherSeries", "VoucherNumber"]
    root_element = "Vouchers"

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "vouchers"


class VoucherDetails(FortnoxSubstream, FortnoxIncrementalStream):
    """
    Voucher details is a substream that reads from substreams.

    First off all financial years are fetched, then the all the vouchers for those years are fetched, after this
    a request for every voucher is made. If there are X financial years, and Y vouchers X+Y+1 requests will be made.

    Thus, it is strongly advised to have incremental sync turned on for this stream.
    """
    primary_key = ["Year", "VoucherSeries", "VoucherNumber"]
    root_element = "Voucher"

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        super_params = super(VoucherDetails, self).request_params(stream_state, stream_slice, next_page_token)
        financial_year = stream_slice.get("parent", {}).get("Year", None)
        if financial_year is not None:
            super_params["financialyear"] = financial_year
        return super_params

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"vouchers/{stream_slice['parent']['VoucherSeries']}/{stream_slice['parent']['VoucherNumber']}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        yield response.json().get("Voucher", {})


class SourceFortnox(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        # auth = FortnoxRefreshingAuthenticator(config)
        # try:
        #     auth.get_access_token()
        # except Exception as e:
        #     return False, f"Got an exception when validating {str(e)}"
        # WARNING: With this authenticator a race-condition may occur when the configuration is refreshed due to new tokens
        # Being issued. Before a sync attempt CHECK is called (in its own docker instance) which emits a configuration change.
        # However, when the READ is issued shortly after it seems like the authenticator is receiving the old configuration
        # information (since the update from the check has not been persisted yet)
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Creates all supported streams

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = FortnoxRefreshingAuthenticator(config)

        financial_years = FinancialYears(authenticator=auth)
        vouchers = Vouchers(parent=financial_years, authenticator=auth)

        return [
            Accounts(parent=financial_years, authenticator=auth),
            CostCenters(authenticator=auth),
            Customers(authenticator=auth),
            Invoices(authenticator=auth),
            Projects(authenticator=auth),
            financial_years,
            vouchers,
            VoucherDetails(parent=vouchers, authenticator=auth),
        ]
