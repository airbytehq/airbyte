from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import datetime
import requests
import pendulum
import json

from dateutil.relativedelta import relativedelta
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator
from source_alipay_worldfirst.auth import RSA256_Signature, get_authorization_header_str, date_time_fmt


# Basic full refresh stream
class AlipayWorldfirstStream(HttpStream, ABC):

    def __init__(
        self,
        url_base: str,
        client_id: str,
        private_key: str,
        period_in_days: Optional[int],
        start_time: Optional[str],
        end_time: Optional[str],
        source_name: str,
        rsa_signature: RSA256_Signature,
    ):
        self._url_base = url_base
        self.client_id = client_id
        self.private_key = private_key
        self.period_in_days = period_in_days
        self.start_time = start_time
        self.end_time = end_time
        self.source_name = source_name
        self.page_index = 1
        self._authenticator = rsa_signature
        self._session = requests.Session()
        self._session.auth = rsa_signature

    @property
    def url_base(self) -> str:
        return self._url_base

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Content-Type": "application/json; charset=UTF-8", "Client-Id": self.client_id}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        yield {}


class StatementList(AlipayWorldfirstStream):

    primary_key = None
    name = "StatementList"

    @property
    def http_method(self) -> str:
        return "POST"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "/amsin/api/v1/business/account/inquiryStatementList"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()
        totalPageNumber = response_json.get("totalPageNumber")
        if self.page_index > totalPageNumber:
            return None
        if "S" == response_json.get("result").get("resultStatus"):
            current_page_number = response_json.get("currentPageNumber")
            total_page_number = response_json.get("totalPageNumber")
            if self.page_index < total_page_number:
                self.page_index += 1
                return {"pageNumber": 1}
        return None

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:

        body = {
            "startTime": "",
            "endTime": "",
            "pageSize": 100,
            "pageNumber": self.page_index,
            "transactionTypeList": ["COLLECTION", "TRANSFER"],
        }
        if self.period_in_days is not None:
            days = self.period_in_days
            today = datetime.date.today()
            end_time = today.strftime(date_time_fmt)
            yesterday = today + relativedelta(days=-1 * days)
            start_time = yesterday.strftime(date_time_fmt)
            body["startTime"] = start_time
            body["endTime"] = end_time
        else:
            body["startTime"] = self.start_time
            body["endTime"] = self.end_time

        return body

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        if "S" == response_json.get("result").get("resultStatus"):
            results = response.json().get("statementList")
            for item in results:
                item["source_name"] = self.source_name
            yield from results
        else:
            raise Exception([{"message": response_json.get("result")}])
