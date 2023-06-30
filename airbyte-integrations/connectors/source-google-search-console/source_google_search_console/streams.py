#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from enum import Enum
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union
from urllib.parse import quote_plus, unquote_plus

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator

BASE_URL = "https://www.googleapis.com/webmasters/v3/"
ROW_LIMIT = 25000


class QueryAggregationType(Enum):
    auto = "auto"
    by_page = "byPage"
    by_property = "byProperty"


class GoogleSearchConsole(HttpStream, ABC):
    url_base = BASE_URL
    primary_key = None
    data_field = ""

    def __init__(
        self,
        authenticator: Union[HttpAuthenticator, requests.auth.AuthBase],
        site_urls: list,
        start_date: str,
        end_date: str,
        data_state: str = "final",
    ):
        super().__init__(authenticator=authenticator)
        self._site_urls = self.sanitize_urls_list(site_urls)
        self._start_date = start_date
        self._end_date = end_date
        self._data_state = data_state

    @staticmethod
    def sanitize_urls_list(site_urls: list) -> List[str]:
        return list(map(quote_plus, site_urls))

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for site_url in self._site_urls:
            yield {"site_url": site_url}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if not self.data_field:
            yield response.json()

        else:
            records = response.json().get(self.data_field) or []
            for record in records:
                yield record


class Sites(GoogleSearchConsole):
    """
    API docs: https://developers.google.com/webmaster-tools/search-console-api-original/v3/sites
    """

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return f"sites/{stream_slice.get('site_url')}"


class Sitemaps(GoogleSearchConsole):
    """
    API docs: https://developers.google.com/webmaster-tools/search-console-api-original/v3/sitemaps
    """

    data_field = "sitemap"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return f"sites/{stream_slice.get('site_url')}/sitemaps"


class SearchAnalytics(GoogleSearchConsole, ABC):
    """
    API docs: https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics
    """

    data_field = "rows"
    aggregation_type = QueryAggregationType.auto
    start_row = 0
    dimensions = []
    search_types = ["web", "news", "image", "video"]
    range_of_days = 3

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return f"sites/{stream_slice.get('site_url')}/searchAnalytics/query"

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return "date"

    @property
    def http_method(self) -> str:
        return "POST"

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        The `stream_slices` implements iterator functionality for `site_urls` and `searchType`. The user can pass many `site_url`,
        and we have to process all of them, we can also pass the` searchType` parameter in the `request body` to get data using some`
        searchType` value from [` web`, `news `,` image`, `video`]. It's just a double nested loop with a yield statement.
        """

        for site_url in self._site_urls:
            for search_type in self.search_types:
                start_date = self._get_start_date(stream_state, site_url, search_type)
                end_date = self._get_end_date()

                if start_date > end_date:
                    start_date = end_date

                next_start = start_date
                period = pendulum.Duration(days=self.range_of_days - 1)
                while next_start <= end_date:
                    next_end = min(next_start + period, end_date)
                    yield {
                        "site_url": site_url,
                        "search_type": search_type,
                        "start_date": next_start.to_date_string(),
                        "end_date": next_end.to_date_string(),
                        "data_state": self._data_state,
                    }
                    # add 1 day for the next slice's start date not to duplicate data from previous slice's end date.
                    next_start = next_end + pendulum.Duration(days=1)

    def next_page_token(self, response: requests.Response) -> Optional[bool]:
        """
        The `next_page_token` implements pagination functionality. This method gets the response
        and compares the number of records with the constant `ROW_LIMITS` (maximum value 25000),
        and if they are equal, this means that we get the end of the` Page`, and we need to go further,
        for this we simply increase the `startRow` parameter in request body by `ROW_LIMIT` value.
        """

        if len(response.json().get(self.data_field, [])) == ROW_LIMIT:
            self.start_row += ROW_LIMIT
            return True

        self.start_row = 0

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Content-Type": "application/json"}

    def request_body_json(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Dict[str, Any], str]]:
        """
        Here is a description of the parameters and implementations of the request body:
        1. The `startDate` is retrieved from the `_get_start_date`,
        if` SyncMode = full_refresh` just use `start_date` from configuration, otherwise use `get_update_state`.
        2. The `endDate` is retrieved from the `config.json`.
        3. The `sizes` parameter is used to group the result by some dimension.
        The following dimensions are available: `date`, `country`, `page`, `device`, `query`.
        4. For the `searchType` check the paragraph stream_slices method.
        5. For the `startRow` and `rowLimit` check next_page_token method.
        """

        data = {
            "startDate": stream_slice["start_date"],
            "endDate": stream_slice["end_date"],
            "dimensions": self.dimensions,
            "searchType": stream_slice.get("search_type"),
            "aggregationType": self.aggregation_type.value,
            "startRow": self.start_row,
            "rowLimit": ROW_LIMIT,
            "dataState": stream_slice.get("data_state"),
        }
        return data

    def _get_end_date(self) -> pendulum.date:
        end_date = pendulum.parse(self._end_date).date()
        # limit `end_date` value with current date
        return min(end_date, pendulum.now().date())

    def _get_start_date(self, stream_state: Mapping[str, Any] = None, site_url: str = None, search_type: str = None) -> pendulum.date:
        start_date = pendulum.parse(self._start_date)

        if start_date and stream_state:
            if stream_state.get(unquote_plus(site_url), {}).get(search_type):
                stream_state_value = stream_state.get(unquote_plus(site_url), {}).get(search_type)

                start_date = max(
                    pendulum.parse(stream_state_value[self.cursor_field]),
                    start_date,
                )

        return start_date.date()

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        records = response.json().get(self.data_field) or []

        for record in records:
            record["site_url"] = unquote_plus(stream_slice.get("site_url"))
            record["search_type"] = stream_slice.get("search_type")

            for dimension in self.dimensions:
                record[dimension] = record["keys"].pop(0)

            # remove unnecessary empty field
            record.pop("keys")

            yield record

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """
        With the existing nested loop implementation, we have to store a `cursor_field` for each `site_url`
        and `searchType`. This functionality is placed in `get_update_state`.

        {
          "stream": {
            "https://domain1.com": {
              "web": {"date": "2022-01-03"},
              "news": {"date": "2022-01-03"},
              "image": {"date": "2022-01-03"},
              "video": {"date": "2022-01-03"}
            },
            "https://domain2.com": {
              "web": {"date": "2022-01-03"},
              "news": {"date": "2022-01-03"},
              "image": {"date": "2022-01-03"},
              "video": {"date": "2022-01-03"}
            },
            "date": "2022-01-03",
          }
        }
        """

        latest_benchmark = latest_record[self.cursor_field]

        site_url = latest_record.get("site_url")
        search_type = latest_record.get("search_type")

        value = current_stream_state.get(site_url, {}).get(search_type, {}).get(self.cursor_field)
        if value:
            latest_benchmark = max(latest_benchmark, value)
        current_stream_state.setdefault(site_url, {}).setdefault(search_type, {})[self.cursor_field] = latest_benchmark

        # we need to get the max date over all searchTypes but the current acceptance test YAML format doesn't
        # support that
        current_stream_state[self.cursor_field] = current_stream_state[site_url][search_type][self.cursor_field]

        return current_stream_state


class SearchAnalyticsByDate(SearchAnalytics):
    dimensions = ["date"]


class SearchAnalyticsByCountry(SearchAnalytics):
    dimensions = ["date", "country"]


class SearchAnalyticsByDevice(SearchAnalytics):
    dimensions = ["date", "device"]


class SearchAnalyticsByPage(SearchAnalytics):
    dimensions = ["date", "page"]


class SearchAnalyticsByQuery(SearchAnalytics):
    dimensions = ["date", "query"]


class SearchAnalyticsAllFields(SearchAnalytics):
    dimensions = ["date", "country", "device", "page", "query"]


class SearchAppearance(SearchAnalytics):
    """
    Dimension searchAppearance can't be used with other dimension.
    search appearance data (AMP, blue link, rich result, and so on) must be queried using a two-step process.
    https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data#search-appearance-data
    """

    dimensions = ["searchAppearance"]


class SearchByKeyword(SearchAnalytics):
    """
    Adds searchAppearance value to dimensionFilterGroups in json body
    https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data#search-appearance-data
    """

    def request_body_json(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Dict[str, Any], str]]:
        data = super().request_body_json(stream_state, stream_slice, next_page_token)

        stream = SearchAppearance(self.authenticator, self._site_urls, self._start_date, self._end_date)
        keywords_records = stream.read_records(sync_mode=SyncMode.full_refresh, stream_state=stream_state, stream_slice=stream_slice)
        keywords = {record["searchAppearance"] for record in keywords_records}

        filters = []
        for keyword in keywords:
            filters.append({"dimension": "searchAppearance", "operator": "equals", "expression": keyword})

        data["dimensionFilterGroups"] = [{"filters": filters}]

        return data


class SearchAnalyticsKeywordPageReport(SearchByKeyword):
    dimensions = ["date", "country", "device", "query", "page"]


class SearchAnalyticsKeywordSiteReportByPage(SearchByKeyword):
    dimensions = ["date", "country", "device", "query"]
    aggregation_type = QueryAggregationType.by_page


class SearchAnalyticsSiteReportBySite(SearchAnalytics):
    dimensions = ["date", "country", "device"]
    aggregation_type = QueryAggregationType.by_property


class SearchAnalyticsSiteReportByPage(SearchAnalytics):
    dimensions = ["date", "country", "device"]
    aggregation_type = QueryAggregationType.by_page


class SearchAnalyticsPageReport(SearchAnalytics):
    dimensions = ["date", "country", "device", "page"]


class SearchAnalyticsByCustomDimensions(SearchAnalytics):
    dimension_to_property_schema_map = {
        "country": [{"country": {"type": ["null", "string"]}}],
        "date": [],
        "device": [{"device": {"type": ["null", "string"]}}],
        "page": [{"page": {"type": ["null", "string"]}}],
        "query": [{"query": {"type": ["null", "string"]}}],
    }

    def __init__(self, dimensions: List[str], *args, **kwargs):
        super(SearchAnalyticsByCustomDimensions, self).__init__(*args, **kwargs)
        self.dimensions = dimensions

    def get_json_schema(self) -> Mapping[str, Any]:
        try:
            return super(SearchAnalyticsByCustomDimensions, self).get_json_schema()
        except FileNotFoundError:
            schema: Mapping[str, Any] = {
                "$schema": "https://json-schema.org/draft-07/schema#",
                "type": ["null", "object"],
                "additionalProperties": True,
                "properties": {
                    "clicks": {"type": ["null", "integer"]},
                    "ctr": {"type": ["null", "number"], "multipleOf": 1e-25},
                    "date": {"type": ["null", "string"], "format": "date"},
                    "impressions": {"type": ["null", "integer"]},
                    "position": {"type": ["null", "number"], "multipleOf": 1e-25},
                    "search_type": {"type": ["null", "string"]},
                    "site_url": {"type": ["null", "string"]},
                },
            }

            dimension_properties = self.dimension_to_property_schema()
            schema["properties"].update(dimension_properties)

            return schema

    def dimension_to_property_schema(self) -> dict:
        properties = {}
        for dimension in sorted(self.dimensions):
            fields = self.dimension_to_property_schema_map[dimension]
            for field in fields:
                properties = {**properties, **field}
        return properties
