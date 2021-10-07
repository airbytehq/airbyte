#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import base64
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator

"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.json file.
"""


# Basic full refresh stream
class SearchMetricsStream(HttpStream, ABC):
    def __init__(self, config: Mapping[str, Any]):
        super().__init__(authenticator=config["authenticator"])
        self.config = config

    primary_key = None
    url_base = "https://api.searchmetrics.com/v4/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        TODO: Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json().get("response", [])

        if isinstance(data, list):
            data = data
        elif isinstance(data, dict):
            data = [data]

        for record in data:
            yield record

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == 400 and "Rankings not yet calculated" in response.json()["error_message"]:
            self.raise_on_http_errors = False
        return super().should_retry(response)

    def raise_on_http_errors(self) -> bool:
        return True


class ChildStreamMixin:
    parent_stream_class: Optional[SearchMetricsStream] = None

    def stream_slices(self, sync_mode, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for item in self.parent_stream_class(config=self.config).read_records(sync_mode=sync_mode):
            for engine in item["engines"]:
                yield {"project_id": item["project_id"], "engine": engine, "project_url": item["project_url"]}

        yield from []


class Projects(SearchMetricsStream):
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "AdminStatusGetListProjects.json"


class ProjectsChildStream(ChildStreamMixin, SearchMetricsStream):
    parent_stream_class = Projects

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {"project_id": stream_slice['project_id'],
                "se_id": stream_slice['engine'],
                "urls": stream_slice['project_url'],
                "url": stream_slice['project_url'],
                "domain": stream_slice['project_url'],
                "countrycode": self.config["country_code"]
                }


class Tags(ProjectsChildStream):
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return f"AdminStatusGetListProjectTags.json"


class BenchmarkRankingsS7(ProjectsChildStream):
    def path(self, **kwargs) -> str:
        return f"ProjectOrganicGetListBenchmarkRankingsS7.json"


class CompetitorRankingsS7(ProjectsChildStream):
    def path(self, **kwargs) -> str:
        return f"ProjectOrganicGetListCompetitorRankingsS7.json"


class DistributionKeywordsS7(ProjectsChildStream):
    def path(self, **kwargs) -> str:
        return f"ProjectOrganicGetListDistributionKeywordsS7.json"


class KeywordPotentialsS7(ProjectsChildStream):
    def path(self, **kwargs) -> str:
        return f"ProjectOrganicGetListKeywordPotentialsS7.json"


class TagPotentialsS7(ProjectsChildStream):
    def path(self, **kwargs) -> str:
        return f"ProjectOrganicGetListTagPotentialsS7.json"


class UrlRankingsS7(ProjectsChildStream):
    def path(self, **kwargs) -> str:
        return f"ProjectOrganicGetListUrlRankingsS7.json"


class MarketshareValueS7(ProjectsChildStream):
    def path(self, **kwargs) -> str:
        return f"ProjectOrganicGetValueMarketshareS7.json"


class SeoVisibilityValueS7(ProjectsChildStream):
    def path(self, **kwargs) -> str:
        return f"ProjectOrganicGetValueSeoVisibilityS7.json"


class SerpSpreadValueS7(ProjectsChildStream):
    def path(self, **kwargs) -> str:
        return f"ProjectOrganicGetValueSerpSpreadS7.json"


class ListCompetitors(ProjectsChildStream):
    def path(self, **kwargs) -> str:
        return f"ResearchOrganicGetListCompetitors.json"


class ListCompetitorsRelevancy(ProjectsChildStream):
    def path(self, **kwargs) -> str:
        return f"ResearchOrganicGetListCompetitorsRelevancy.json"


class ListRankingsDomain(ProjectsChildStream):
    def path(self, **kwargs) -> str:
        return f"ResearchOrganicGetListRankingsDomain.json"


class ListSeoVisibilityCountry(ProjectsChildStream):
    def path(self, **kwargs) -> str:
        return f"ResearchOrganicGetListSeoVisibilityCountry.json"


class ListLosersS7(ProjectsChildStream):
    def path(self, **kwargs) -> str:
        return f"ProjectOrganicGetListLosersS7.json"


class ListMarketShareS7(ProjectsChildStream):
    def path(self, **kwargs) -> str:
        return f"ProjectOrganicGetListMarketShareS7.json"


class ListPositionSpreadHistoricS7(ProjectsChildStream):
    def path(self, **kwargs) -> str:
        return f"ProjectOrganicGetListPositionSpreadHistoricS7.json"


class ListSeoVisibilityHistoricS7(ProjectsChildStream):
    def path(self, **kwargs) -> str:
        return f"ProjectOrganicGetListSeoVisibilityHistoricS7.json"


class ListRankingsAnalysisS7(ProjectsChildStream):
    def path(self, **kwargs) -> str:
        return f"ProjectOrganicGetListRankingsAnalysisS7.json"


class ListWinnersS7(ProjectsChildStream):
    def path(self, **kwargs) -> str:
        return f"ProjectOrganicGetListWinnersS7.json"


class ListRankingsHistoricS7(ProjectsChildStream):
    def path(self, **kwargs) -> str:
        return f"ProjectOrganicGetListRankingsHistoricS7.json"


class ListSerpSpreadS7(ProjectsChildStream):
    def path(self, **kwargs) -> str:
        return f"ProjectOrganicGetListSerpSpreadS7.json"


class SearchMetricsAuthenticator(Oauth2Authenticator):
    def __init__(self, config):
        super().__init__(
            token_refresh_endpoint="https://api.searchmetrics.com/v4/token",
            client_id=config["api_key"],
            client_secret=config["client_secret"],
            refresh_token=None,
        )

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        payload: MutableMapping[str, Any] = {
            "grant_type": "client_credentials"
        }

        return payload

    def get_refresh_request_headers(self) -> Mapping[str, Any]:
        encoded_credentials = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode("ascii"))
        headers: MutableMapping[str, Any] = {
            "Accept": "application/json",
            "Authorization": f"Basic {encoded_credentials.decode('utf-8')}"
        }

        return headers

    def refresh_access_token(self) -> Tuple[str, int]:
        """
        Returns a tuple of (access_token, token_lifespan_in_seconds)
        """
        try:
            response = requests.request(method="POST", url=self.token_refresh_endpoint, headers=self.get_refresh_request_headers(), data=self.get_refresh_request_body())
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
            url = f"https://api.searchmetrics.com/v4/AdminStatusGetListProjects.json"

            auth_headers = {"Accept": "application/json", **authenticator.get_auth_header()}
            session = requests.get(url, headers=auth_headers)
            session.raise_for_status()

            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config["authenticator"] = SearchMetricsAuthenticator(config)
        return [Projects(config),
                Tags(config),
                BenchmarkRankingsS7(config),
                CompetitorRankingsS7(config),
                DistributionKeywordsS7(config),
                KeywordPotentialsS7(config),
                TagPotentialsS7(config),
                UrlRankingsS7(config),
                SeoVisibilityValueS7(config),
                SerpSpreadValueS7(config),
                ListCompetitors(config),
                ListCompetitorsRelevancy(config),
                ListRankingsDomain(config),
                ListSeoVisibilityCountry(config),
                ListLosersS7(config),
                # ListMarketShareS7(config),
                # ListPositionSpreadHistoricS7(config),
                # ListSeoVisibilityHistoricS7(config),
                ListWinnersS7(config),
                ListRankingsHistoricS7(config),
                ListSerpSpreadS7(config),
                ]


"""
    ProjectOrganicGetListLosersS7
    ProjectOrganicGetListMarketShareS7
    ProjectOrganicGetListPositionSpreadHistoricS7
    ProjectOrganicGetListSeoVisibilityHistoricS7
    ProjectOrganicGetListWinnersS7
    
    ProjectOrganicGetListRankingsAnalysisS7
    ProjectOrganicGetListRankingsHistoricS7
    ProjectOrganicGetListSerpSpreadS7


"""
