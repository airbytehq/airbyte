#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from datetime import date, datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import backoff
import requests

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


class KyribaClient:
    def __init__(self, username: str, password: str, gateway_url: str):
        self.username = username
        self.password = password
        self.url = f"{gateway_url}/oauth/token"

    def login(self) -> TokenAuthenticator:
        data = {"grant_type": "client_credentials"}
        auth = requests.auth.HTTPBasicAuth(self.username, self.password)
        response = requests.post(self.url, auth=auth, data=data)
        response.raise_for_status()
        self.access_token = response.json()["access_token"]
        return TokenAuthenticator(self.access_token)


# Basic full refresh stream
class KyribaStream(HttpStream):
    def __init__(
        self,
        gateway_url: str,
        client: KyribaClient,
        start_date: str,
        end_date: str = None,
    ):
        self.gateway_url = gateway_url
        self.start_date = date.fromisoformat(start_date) or date.today()
        self.end_date = date.fromisoformat(end_date) if end_date else None
        self.client = client
        super().__init__(self.client.login())

    primary_key = None

    @property
    def url_base(self) -> str:
        return f"{self.gateway_url}/api/v1/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        metadata = response.json()["metadata"]
        next_page = metadata["links"].get("next")
        next_offset = metadata["pageOffset"] + metadata["pageLimit"]
        return {"page.offset": next_offset} if next_page else None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return next_page_token

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=3)
    def should_retry(self, response: requests.Response) -> bool:
        # Kyriba uses basic auth to generate an expiring bearer token
        # There is no refresh token, so users need to log in again when the token expires
        if response.status_code == 401:
            self._session.auth = self.client.login()
            response.request.headers["Authorization"] = f"Bearer {self.client.access_token}"
            # change the response status code to 571, so should_give_up in rate_limiting.py
            # does not evaluate to true
            response.status_code = 571
            return True
        return response.status_code == 429 or 500 <= response.status_code < 600

    def unnest(self, key: str, data: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Kyriba loves to nest fields, but nested fields cannot be used in an
        incremental cursor. This method grabs the hash where the increment field
        is nested and puts it at the top level
        """
        nested = data.pop(key)
        return {**data, **nested}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        results = response.json().get("results")
        for result in results:
            yield result


# Basic incremental stream
class IncrementalKyribaStream(KyribaStream, ABC):
    cursor_field = "updateDateTime"

    # Checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    @property
    def state_checkpoint_interval(self) -> int:
        # 100 is the default page size
        return 100

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_cursor = latest_record.get(self.cursor_field) or ""
        current_cursor = current_stream_state.get(self.cursor_field) or ""
        return {self.cursor_field: max(current_cursor, latest_cursor)}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"sort": self.cursor_field}
        latest_cursor = stream_state.get(self.cursor_field) or self.start_date.isoformat() + "T00:00:00Z"
        if latest_cursor:
            filter = f"{self.cursor_field}=gt='{latest_cursor}'"
            params["filter"] = filter
        if next_page_token:
            params = {**params, **next_page_token}
        return params


class Accounts(KyribaStream):
    primary_key = "uuid"
    use_cache = True

    def path(self, **kwargs) -> str:
        return "accounts"


class AccountSubStream(HttpSubStream, KyribaStream):
    def __init__(self, **kwargs):
        super().__init__(parent=Accounts, **kwargs)
        self.parent = Accounts(**kwargs)

    def get_account_uuids(self) -> Iterable[Optional[Mapping[str, str]]]:
        return [{"account_uuid": a["uuid"]} for a in self.parent.read_records(sync_mode=SyncMode.full_refresh)]

    def next_page_token(self, response: requests.Response):
        pass

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield response.json()


class CashBalancesStream(AccountSubStream):
    def stream_slices(
        self, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        slices = []
        account_uuids = self.get_account_uuids()
        # we can query a max of 31 days at a time
        days_inc = 31
        start_date = self.start_date
        end_date = self.end_date or date.today()
        while start_date <= end_date:
            seg_end_date = start_date + timedelta(days=days_inc)
            seg_end_date = seg_end_date if seg_end_date <= end_date else end_date
            date_params = {
                "startDate": start_date.isoformat(),
                "endDate": seg_end_date.isoformat(),
            }
            slices.extend([{**u, **date_params} for u in account_uuids])
            # ensure the next start date is never greater than today since we are getting EOD balances
            start_date = seg_end_date + timedelta(days=1)
        return slices

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        account_uuid = stream_slice["account_uuid"]
        return f"cash-balances/accounts/{account_uuid}/balances"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            "endDate": stream_slice["endDate"],
            "startDate": stream_slice["startDate"],
            "intraday": self.intraday,
            "actual": True,
            "estimatedForecasts": False,
            "confirmedForecasts": False,
            "dateType": "VALUE",
        }


class CashBalancesEod(CashBalancesStream):
    intraday = False


class CashBalancesIntraday(CashBalancesStream):
    intraday = True


class BankBalancesStream(AccountSubStream):
    def stream_slices(
        self, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        slices = []
        account_uuids = self.get_account_uuids()
        # bank balances require the date to be specified
        bal_date = self.start_date
        end_date = self.end_date or date.today()
        while bal_date <= end_date:
            slices.extend([{**u, "date": bal_date.isoformat()} for u in account_uuids])
            bal_date = bal_date + timedelta(days=1)
        return slices

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        account_uuid = stream_slice["account_uuid"]
        return f"bank-balances/accounts/{account_uuid}/balances"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            "date": stream_slice["date"],
            "type": self.balance_type,
        }


class BankBalancesEod(BankBalancesStream):
    balance_type = "END_OF_DAY"


class BankBalancesIntraday(BankBalancesStream):
    balance_type = "INTRADAY"


class CashFlows(IncrementalKyribaStream):
    primary_key = "uuid"

    def path(self, **kwargs) -> str:
        return "cash-flows"

    def stream_slices(
        self, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        end_date = self.end_date or date.today()
        if stream_state and stream_state.get(self.cursor_field):
            latest = stream_state.get(self.cursor_field)
            start = datetime.strptime(latest, "%Y-%m-%dT%H:%M:%SZ").date()
            # produce at least one slice with abnormal state
            start = start if start <= end_date else end_date
        else:
            start = self.start_date
        slices = []
        while start <= end_date:
            # use small slices to maintain state since the API is unreliable
            end = start if start < end_date else end_date
            slices.append({"startDate": start.isoformat(), "endDate": end.isoformat()})
            start = end + timedelta(days=1)
        return slices

    def request_params(self, stream_slice: Optional[Mapping[str, Any]], **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs) or {}
        params["dateType"] = "UPDATE"
        params["page.limit"] = 1000
        params = {**params, **stream_slice}
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # the updatedDateTime is unnecessarily nested under date
        # Airbyte cannot accomodate nested cursors, so this needs to be fixed
        results = response.json().get("results")
        for result in results:
            yield self.unnest("date", result)


# Source
class SourceKyriba(AbstractSource):
    def gateway_url(self, config: Mapping[str, Any]) -> str:
        return f"https://{config['domain']}/gateway"

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            client = KyribaClient(config["username"], config["password"], self.gateway_url(config))
            client.login()
            return True, None
        except Exception as e:
            if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 401:
                err_message = f"Please check your `username` and `password`. Error: {repr(e)}"
                return False, err_message
            return False, repr(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        gateway_url = self.gateway_url(config)
        client = KyribaClient(config["username"], config["password"], gateway_url)
        kwargs = {
            "gateway_url": gateway_url,
            "client": client,
            "start_date": config.get("start_date"),
            "end_date": config.get("end_date"),
        }
        return [
            Accounts(**kwargs),
            CashFlows(**kwargs),
            CashBalancesEod(**kwargs),
            CashBalancesIntraday(**kwargs),
            BankBalancesEod(**kwargs),
            BankBalancesIntraday(**kwargs),
        ]
