#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream

from .utils import (
    authenticator_class_map,
    page_performance_request_body,
    flatten_report_pages_performance_data,
)


class GoogleAnalyticsArcaneStream(HttpStream, ABC):

    url_base = "https://analyticsdata.googleapis.com/v1beta/"
    http_method = "POST"
    raise_on_http_errors = True
    primary_key = None
    offset = 0

    def __init__(self, *, config: Mapping[str, Any], page_size: int = 100_000, **kwargs):
        super().__init__(**kwargs)
        self._config = config
        # default value is 100 000 due to determination of maximum limit value in official documentation
        # https://developers.google.com/analytics/devguides/reporting/data/v1/basics#pagination
        self._page_size = page_size

    @property
    def config(self):
        return self._config

    @property
    def page_size(self):
        return self._page_size

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        r = response.json()

        if "rowCount" in r:
            total_rows = r["rowCount"]

            if self.offset == 0:
                self.offset = self.page_size
            else:
                self.offset += self.page_size

            if total_rows <= self.offset:
                self.offset = 0
                return

            return {"offset": self.offset}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return {}

    @property
    def start_date_as_string(self):
        """ Return the date in the YYYY-MM-DD format"""
        return self.config["start_date"]


class GoogleAnalyticsArcaneAdminAPIStream(GoogleAnalyticsArcaneStream, ABC):
    url_base = "https://analyticsadmin.googleapis.com/v1beta/"
    http_method = "GET"

    offset = 0

    @property
    def page_size(self):
        return self._page_size

    @property
    def account_id(self):
        return self.config["account_id"]


class Accounts(GoogleAnalyticsArcaneAdminAPIStream):
    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        account_id = self.account_id
        return f"accounts/{account_id}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = [response.json()]
        yield from response_json


class Properties(GoogleAnalyticsArcaneAdminAPIStream):

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return "properties"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        params = {"filter": f"parent:accounts/{self.account_id}"}
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get("properties")


class ReportPagesPerformance(GoogleAnalyticsArcaneStream):

    parent_stream = Properties

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return f"properties/{stream_slice['property_id']}:runReport"

    def request_body_json(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        request_body: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping[str, Any]]:
        payload = {
                "metrics": [{"name": m} for m in page_performance_request_body["metrics"]],
                "dimensions": [{"name": m} for m in page_performance_request_body["dimensions"]],
                "orderBys": page_performance_request_body["orderBys"],
                "dateRanges": [{
                    "endDate": "today",
                    "startDate": self.start_date_as_string,
                    }
                ]
            }

        if next_page_token and next_page_token.get("offset") is not None:
            payload.update({"offset": str(next_page_token["offset"])})
        return payload

    def parse_response(self, response: requests.Response, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping]:
        response_json = [response.json()]
        # self.logger.info(f"{self.__class__.__name__} : parse_response : {response_json}")
        flattened_data = flatten_report_pages_performance_data(response_json)
        if flattened_data:
            for row in flattened_data:
                row["propertyId"] = stream_slice["property_id"]
            yield from flattened_data
        else:
            return

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        # property_ids = ["374198151", "396002141", "411004107"]
        parent_stream = self.parent_stream(authenticator=self.authenticator, config=self.config)
        for record in parent_stream.read_records(sync_mode=SyncMode.full_refresh):
            property_id = record["name"].split('/')[1]
            yield {"property_id": property_id}


# Source
class SourceGoogleAnalyticsArcane(AbstractSource):

    def get_authenticator(self, config: Mapping[str, Any]):
        credentials = config["credentials"]
        authenticator_class, get_credentials = authenticator_class_map[credentials["auth_type"]]
        return authenticator_class(**get_credentials(credentials))

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        python main.py check --config secrets/config.json
        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        _config = config.copy()
        _config["authenticator"] = self.get_authenticator(_config)
        admin_stream = Accounts(config=_config, authenticator=_config["authenticator"])
        try:
            next(admin_stream.read_records(sync_mode=SyncMode.full_refresh), None)
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Define each stream class
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = self.get_authenticator(config)
        return [
            Accounts(authenticator=auth, config=config),
            Properties(authenticator=auth, config=config),
            ReportPagesPerformance(authenticator=auth, config=config),
        ]
