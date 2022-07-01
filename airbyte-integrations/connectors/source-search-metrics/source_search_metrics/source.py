#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import base64
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator

from .utils import to_datetime_str


class SearchMetricsStream(HttpStream, ABC):
    primary_key = None
    page_size = 250
    url_base = "https://api.searchmetrics.com/v4/"

    def __init__(self, config: Mapping[str, Any]):
        super().__init__(authenticator=config["authenticator"])
        self.config = config
        self.start_date = config["start_date"]
        self.window_in_days = config.get("window_in_days", 30)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {
            "project_id": stream_slice["project_id"],
            "se_id": stream_slice["engine"],
            "urls": stream_slice["project_url"],
            "url": stream_slice["project_url"],
            "domain": stream_slice["project_url"],
            "countrycode": self.config["country_code"],
            "limit": self.page_size,
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json().get("response", [])

        if isinstance(data, list):
            data = data
        elif isinstance(data, dict):
            data = [data]

        for record in data:
            yield record

    def should_retry(self, response: requests.Response) -> bool:
        rankings_not_yet_calculated = response.status_code == 400 and "Rankings not yet calculated" in response.json()["error_message"]
        insufficient_credits_to_make_this_service_request = (
            response.status_code == 403 and "Insufficient credits to make this service request" in response.json()["error_message"]
        )

        if rankings_not_yet_calculated or insufficient_credits_to_make_this_service_request:
            self.logger.error(f"{response.json()['error_message']}")
            self.raise_on_http_errors = False

        return super().should_retry(response)

    def raise_on_http_errors(self) -> bool:
        return True


class ChildStreamMixin:
    parent_stream_class: Optional[SearchMetricsStream] = None

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for item in self.parent_stream_class(config=self.config).read_records(sync_mode=None):
            for engine in item["engines"]:
                yield {"project_id": item["project_id"], "engine": engine, "project_url": item["project_url"]}

        yield from []


class Projects(SearchMetricsStream):
    primary_key = "project_id"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {}

    def path(self, **kwargs) -> str:
        return "AdminStatusGetListProjects.json"


class ProjectsChildStream(ChildStreamMixin):
    parent_stream_class = Projects


class IncrementalSearchMetricsStream(ProjectsChildStream, SearchMetricsStream):
    cursor_field = "date"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["date_from"] = stream_slice["date_from"]
        params["date_to"] = stream_slice["date_to"]
        return params

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            self.cursor_field: max(
                str(latest_record.get(self.cursor_field, self.start_date)),
                str(current_stream_state.get(self.cursor_field, self.start_date)),
            )
        }

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Override default stream_slices CDK method to provide date_slices as page chunks for data fetch.
        Returns list of dict, example: [{
            "date_from": "20200101",
            "date_to": "20210102"
            },
            {
            "date_from": "20200103",
            "date_to": "20210104"
            },
            ...]
        """

        for stream_slice in super().stream_slices(**kwargs):
            start_date = pendulum.parse(self.start_date).date()
            end_date = pendulum.now().date()

            # Determine stream_state, if no stream_state we use start_date
            if stream_state:
                start_date = pendulum.parse(stream_state.get(self.cursor_field)).date()

            # use the lowest date between start_date and self.end_date, otherwise API fails if start_date is in future
            start_date = min(start_date, end_date)
            date_slices = []

            while start_date <= end_date:
                end_date_slice = start_date.add(days=self.window_in_days)
                stream_slice.update({"date_from": to_datetime_str(start_date), "date_to": to_datetime_str(min(end_date_slice, end_date))})
                date_slices.append(stream_slice)
                # add 1 day for start next slice from next day and not duplicate data from previous slice end date.
                start_date = end_date_slice.add(days=1)

            return date_slices


class Tags(ProjectsChildStream, SearchMetricsStream):
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "AdminStatusGetListProjectTags.json"


class BenchmarkRankingsS7(ProjectsChildStream, SearchMetricsStream):
    def path(self, **kwargs) -> str:
        return "ProjectOrganicGetListBenchmarkRankingsS7.json"


class CountDomainKeyword(ProjectsChildStream, SearchMetricsStream):
    def path(self, **kwargs) -> str:
        return "ResearchOrganicGetCountDomainKeyword.json"


class CompetitorRankingsS7(ProjectsChildStream, SearchMetricsStream):
    def path(self, **kwargs) -> str:
        return "ProjectOrganicGetListCompetitorRankingsS7.json"


class DistributionKeywordsS7(ProjectsChildStream, SearchMetricsStream):
    def path(self, **kwargs) -> str:
        return "ProjectOrganicGetListDistributionKeywordsS7.json"


class KeywordPotentialsS7(ProjectsChildStream, SearchMetricsStream):
    def path(self, **kwargs) -> str:
        return "ProjectOrganicGetListKeywordPotentialsS7.json"


class TagPotentialsS7(ProjectsChildStream, SearchMetricsStream):
    def path(self, **kwargs) -> str:
        return "ProjectOrganicGetListTagPotentialsS7.json"


class UrlRankingsS7(ProjectsChildStream, SearchMetricsStream):
    def path(self, **kwargs) -> str:
        return "ProjectOrganicGetListUrlRankingsS7.json"


class MarketshareValueS7(ProjectsChildStream, SearchMetricsStream):
    def path(self, **kwargs) -> str:
        return "ProjectOrganicGetValueMarketshareS7.json"


class SeoVisibilityValueS7(ProjectsChildStream, SearchMetricsStream):
    def path(self, **kwargs) -> str:
        return "ProjectOrganicGetValueSeoVisibilityS7.json"


class SerpSpreadValueS7(ProjectsChildStream, SearchMetricsStream):
    def path(self, **kwargs) -> str:
        return "ProjectOrganicGetValueSerpSpreadS7.json"


class ListCompetitors(ProjectsChildStream, SearchMetricsStream):
    def path(self, **kwargs) -> str:
        return "ResearchOrganicGetListCompetitors.json"


class ListCompetitorsRelevancy(ProjectsChildStream, SearchMetricsStream):
    def path(self, **kwargs) -> str:
        return "ResearchOrganicGetListCompetitorsRelevancy.json"


class ListRankingsDomain(ProjectsChildStream, SearchMetricsStream):
    def path(self, **kwargs) -> str:
        return "ResearchOrganicGetListRankingsDomain.json"


class ListSeoVisibilityCountry(ProjectsChildStream, SearchMetricsStream):
    def path(self, **kwargs) -> str:
        return "ResearchOrganicGetListSeoVisibilityCountry.json"


class ListLosersS7(ProjectsChildStream, SearchMetricsStream):
    def path(self, **kwargs) -> str:
        return "ProjectOrganicGetListLosersS7.json"


class ListMarketShareS7(IncrementalSearchMetricsStream):
    def path(self, **kwargs) -> str:
        return "ProjectOrganicGetListMarketShareS7.json"


class ListPositionSpreadHistoricS7(IncrementalSearchMetricsStream):
    def path(self, **kwargs) -> str:
        return "ProjectOrganicGetListPositionSpreadHistoricS7.json"


class ListSeoVisibilityHistoricS7(IncrementalSearchMetricsStream):
    def path(self, **kwargs) -> str:
        return "ProjectOrganicGetListSeoVisibilityHistoricS7.json"


class ListRankingsAnalysisS7(ProjectsChildStream, SearchMetricsStream):
    def path(self, **kwargs) -> str:
        return "ProjectOrganicGetListRankingsAnalysisS7.json"


class ListWinnersS7(ProjectsChildStream, SearchMetricsStream):
    def path(self, **kwargs) -> str:
        return "ProjectOrganicGetListWinnersS7.json"


class ListRankingsHistoricS7(ProjectsChildStream, SearchMetricsStream):
    def path(self, **kwargs) -> str:
        return "ProjectOrganicGetListRankingsHistoricS7.json"


class ListSerpSpreadS7(ProjectsChildStream, SearchMetricsStream):
    def path(self, **kwargs) -> str:
        return "ProjectOrganicGetListSerpSpreadS7.json"


class SearchMetricsAuthenticator(Oauth2Authenticator):
    def __init__(self, config):
        super().__init__(
            token_refresh_endpoint="https://api.searchmetrics.com/v4/token",
            client_id=config["api_key"],
            client_secret=config["client_secret"],
            refresh_token=None,
        )

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        payload: MutableMapping[str, Any] = {"grant_type": "client_credentials"}

        return payload

    def get_refresh_request_headers(self) -> Mapping[str, Any]:
        encoded_credentials = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode("ascii"))
        headers: MutableMapping[str, Any] = {"Accept": "application/json", "Authorization": f"Basic {encoded_credentials.decode('utf-8')}"}

        return headers

    def refresh_access_token(self) -> Tuple[str, int]:
        """
        Returns a tuple of (access_token, token_lifespan_in_seconds)
        """
        try:
            response = requests.request(
                method="POST",
                url=self.token_refresh_endpoint,
                headers=self.get_refresh_request_headers(),
                data=self.get_refresh_request_body(),
            )
            response.raise_for_status()
            response_json = response.json()
            return response_json["access_token"], response_json["expires_in"]
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e


# Source
class SourceSearchMetrics(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Testing connection availability for the connector by granting the credentials.
        """
        authenticator = SearchMetricsAuthenticator(config)

        try:
            url = "https://api.searchmetrics.com/v4/AdminStatusGetListProjects.json"

            auth_headers = {"Accept": "application/json", **authenticator.get_auth_header()}
            session = requests.get(url, headers=auth_headers)
            session.raise_for_status()

            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config["authenticator"] = SearchMetricsAuthenticator(config)
        return [
            BenchmarkRankingsS7(config),
            CompetitorRankingsS7(config),
            CountDomainKeyword(config),
            DistributionKeywordsS7(config),
            KeywordPotentialsS7(config),
            ListCompetitors(config),
            ListCompetitorsRelevancy(config),
            ListLosersS7(config),
            ListMarketShareS7(config),
            ListPositionSpreadHistoricS7(config),
            ListRankingsDomain(config),
            ListRankingsHistoricS7(config),
            ListSeoVisibilityCountry(config),
            ListSeoVisibilityHistoricS7(config),
            ListSerpSpreadS7(config),
            ListWinnersS7(config),
            Projects(config),
            SeoVisibilityValueS7(config),
            SerpSpreadValueS7(config),
            TagPotentialsS7(config),
            Tags(config),
            UrlRankingsS7(config),
        ]
