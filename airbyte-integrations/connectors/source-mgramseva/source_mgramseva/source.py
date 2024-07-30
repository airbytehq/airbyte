#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import base64
from datetime import datetime
from logging import Logger
import requests
import pytz
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


# Basic full refresh stream
class MgramsevaStream(HttpStream, ABC):
    """Base for all objects"""

    url_base = "https://www.peyjalbihar.org/"

    http_method = "POST"

    primary_key = "id"

    def __init__(self, endpoint: str, headers: dict, request_info: dict, user_request: dict, params: dict, response_key: str, **kwargs):
        """set base url, headers, request info and user request"""
        super().__init__(**kwargs)
        self.endpoint = endpoint
        self.headers = headers
        self.request_info = request_info
        self.user_request = user_request
        self.params = params
        self.response_key = response_key

    def path(
        self,
        stream_state: Mapping[str, Any] = None,  # pylint: disable=unused-argument
        stream_slice: Mapping[str, Any] = None,  # pylint: disable=unused-argument
        next_page_token: Mapping[str, Any] = None,  # pylint: disable=unused-argument
    ) -> str:
        """path"""
        return self.endpoint

    def request_headers(
        self,
        stream_state: Optional[Mapping[str, Any]],  # pylint: disable=unused-argument
        stream_slice: Optional[Mapping[str, Any]] = None,  # pylint: disable=unused-argument
        next_page_token: Optional[Mapping[str, Any]] = None,  # pylint: disable=unused-argument
    ) -> Mapping[str, Any]:
        """Return headers required for the request"""
        return self.headers

    def request_body_json(
        self,
        stream_state: Optional[Mapping[str, Any]],  # pylint: disable=unused-argument
        stream_slice: Optional[Mapping[str, Any]] = None,  # pylint: disable=unused-argument
        next_page_token: Optional[Mapping[str, Any]] = None,  # pylint: disable=unused-argument
    ) -> Optional[Mapping[str, Any]]:
        """
        All requests require the same body
        """
        return {"RequestInfo": self.request_info, "userInfo": self.user_request}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        TODO: Override this method to define a pagination strategy. If you will not be using pagination, no action is required - just return None.

        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],  # pylint: disable=unused-argument
        stream_slice: Mapping[str, any] = None,  # pylint: disable=unused-argument
        next_page_token: Mapping[str, Any] = None,  # pylint: disable=unused-argument
    ) -> MutableMapping[str, Any]:
        """request parameters"""
        return self.params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        return map(lambda x: {"data": x, "id": x["id"]}, response.json()[self.response_key])

    # def base_schema(self) -> dict:
    #     """Base schema for all streams"""
    #     return {
    #         "$schema": "http://json-schema.org/draft-07/schema#",
    #         "type": "object",
    #         "properties": {"id": {"type": "string"}, "data": {"type": "object"}},
    #     }


class MgramsevaDemands(MgramsevaStream):
    """object for consumer demands"""

    def __init__(self, headers: dict, request_info: dict, user_request: dict, start_date: datetime, end_date: datetime, **kwargs):
        """specify endpoint for demands and call super"""
        params = {
            "tenantId": "br.testing",
            "businessService": "WS",
            "periodFrom": int(1000 * start_date.timestamp()),
            "periodTo": int(1000 * end_date.timestamp()),
        }
        super().__init__("billing-service/demand/_search", headers, request_info, user_request, params, "Demands", **kwargs)


class MgramsevaBills(MgramsevaStream):
    """object for consumer bills"""

    @property
    def name(self) -> str:
        return f"Bill_{self.consumer_code.replace('/', '_')}"

    def get_json_schema(self) -> Mapping[str, Any]:
        """override"""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {"id": {"type": "string"}, "data": {"type": "object"}},
        }

    def __init__(self, headers: dict, request_info: dict, user_request: dict, consumer_code: str, **kwargs):
        """specify endpoint for bills and call super"""
        self.consumer_code = consumer_code
        params = {
            "tenantId": "br.testing",
            "consumerCode": consumer_code,
            "businessService": "WS",
        }
        super().__init__("billing-service/bill/v2/_fetchbill", headers, request_info, user_request, params, "Bill", **kwargs)


class MgramsevaTenantExpenses(MgramsevaStream):
    """object for tenant payments"""

    def __init__(self, headers: dict, request_info: dict, user_request: dict, **kwargs):
        """
        specify endpoint for demands and call super
        1672531200000 = 2023-01-01 00:00
        1830297600000 = 2028-01-01 00:00
        """
        params = {"tenantId": "br.testing", "fromDate": 1672531200000, "toDate": 1830297600000}
        super().__init__(
            "echallan-services/eChallan/v1/_expenseDashboard", headers, request_info, user_request, params, "ExpenseDashboard", **kwargs
        )

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :this response has only one object, so return it
        """
        return [{"data": response.json()[self.response_key], "id": "1"}]


class MgramsevaPayments(MgramsevaStream):
    """object for consumer payments"""

    def __init__(self, headers: dict, request_info: dict, user_request: dict, **kwargs):
        """specify endpoint for payments and call super"""
        params = {"tenantId": "br.testing", "businessService": "WS"}
        super().__init__("collection-services/payments/WS/_search", headers, request_info, user_request, params, "Payments", **kwargs)


# Source
class SourceMgramseva(AbstractSource):
    """Source for mGramSeva"""

    def __init__(self):
        """constructor"""
        self.headers = {}
        self.request_info = {}
        self.user_request = {}
        self.base_url = None
        self.config = {}
        self.setup_complete = False

    def setup(self, config: dict) -> None:
        """
        config contains
        - base_url
        - client_user
        - client_password
        - username
        - password
        """
        if self.setup_complete:
            return
        if config["client_password"] == "no-pass":
            config["client_password"] = ""
        client_user_password = f'{config["client_user"]}:{config["client_password"]}'
        apikey = base64.encodebytes(client_user_password.encode("ascii")).decode("utf-8").strip()
        self.headers = {"Authorization": "Basic " + apikey}

        base_url = config["base_url"]
        if base_url[-1] != "/":
            base_url += "/"
        self.base_url = base_url

        self.config = config
        self.setup_complete = True

    def get_auth_token(self) -> None:
        """performs the auth step to get the access token and the user info"""

        response = requests.post(
            self.base_url + "user/oauth/token",
            params={
                "username": self.config["username"],
                "password": self.config["password"],
                "scope": "read",
                "grant_type": "password",
                "tenantId": "br",
                "userType": "EMPLOYEE",
            },
            headers=self.headers,
            timeout=15,
        )

        response.raise_for_status()

        auth_response = response.json()
        self.user_request = auth_response["UserRequest"]
        self.request_info = {
            "action": "_search",
            "apiId": "mgramseva",
            "authToken": auth_response["access_token"],
            "userInfo": self.user_request,
        }

    def check_connection(self, logger: Logger, config) -> Tuple[bool, any]:
        """attempt to connect to the API with the provided credentials"""
        try:
            self.setup(config)
            self.get_auth_token()
        except requests.HTTPError as e:
            logger.exception(e)
            return False, str(e)
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """return all the streams we have to sync"""

        self.setup(config)
        self.get_auth_token()

        # Generate streams for each object type
        streams = [
            MgramsevaPayments(self.headers, self.request_info, self.user_request),
            MgramsevaTenantExpenses(self.headers, self.request_info, self.user_request),
        ]

        start_date = datetime.strptime(config.get("start_date", "2022-01-01"), "%Y-%m-%d").replace(tzinfo=pytz.UTC)
        end_date = datetime.today().replace(tzinfo=pytz.UTC)

        demand_stream = MgramsevaDemands(self.headers, self.request_info, self.user_request, start_date, end_date)
        streams.append(demand_stream)

        # and now we need bills for each consumer
        consumer_codes = set()
        for demand in demand_stream.read_records(SyncMode.full_refresh):
            if demand["data"]["consumerCode"] not in consumer_codes:
                consumer_codes.add(demand["data"]["consumerCode"])
                streams.append(MgramsevaBills(self.headers, self.request_info, self.user_request, demand["data"]["consumerCode"]))

        return streams
