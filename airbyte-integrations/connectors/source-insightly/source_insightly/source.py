#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import BasicHttpAuthenticator
from requests.auth import AuthBase

PAGE_SIZE = 500
BASE_URL = "https://api.insightly.com/v3.1/"


# Basic full refresh stream
class InsightlyStream(HttpStream, ABC):
    total_count: int = 0
    page_size: Optional[int] = PAGE_SIZE

    url_base = BASE_URL

    def __init__(self, authenticator: AuthBase, start_date: str = None, **kwargs):
        self.start_date = start_date
        super().__init__(authenticator=authenticator)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        parsed = urlparse(response.request.url)
        previous_skip = parse_qs(parsed.query)["skip"][0]
        new_skip = int(previous_skip) + self.page_size
        return new_skip if new_skip <= self.total_count else None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            "count_total": True,
            "top": self.page_size,
            "skip": next_page_token or 0,
        }

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Accept": "application/json"}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        self.total_count = int(response.headers.get("X-Total-Count", 0))
        results = response.json()
        yield from results


class ActivitySets(InsightlyStream):
    primary_key = "ACTIVITYSET_ID"

    def path(self, **kwargs) -> str:
        return "ActivitySets"


class Countries(InsightlyStream):
    primary_key = "COUNTRY_NAME"

    def path(self, **kwargs) -> str:
        return "Countries"


class Currencies(InsightlyStream):
    primary_key = "CURRENCY_CODE"

    def path(self, **kwargs) -> str:
        return "Currencies"


class Emails(InsightlyStream):
    primary_key = "EMAIL_ID"

    def path(self, **kwargs) -> str:
        return "Emails"


class LeadSources(InsightlyStream):
    primary_key = "LEAD_SOURCE_ID"

    def path(self, **kwargs) -> str:
        return "LeadSources"


class LeadStatuses(InsightlyStream):
    primary_key = "LEAD_STATUS_ID"

    def path(self, **kwargs) -> str:
        return "LeadStatuses"


class OpportunityCategories(InsightlyStream):
    primary_key = "CATEGORY_ID"

    def path(self, **kwargs) -> str:
        return "OpportunityCategories"


class OpportunityStateReasons(InsightlyStream):
    primary_key = "STATE_REASON_ID"

    def path(self, **kwargs) -> str:
        return "OpportunityStateReasons"


class Pipelines(InsightlyStream):
    primary_key = "PIPELINE_ID"

    def path(self, **kwargs) -> str:
        return "Pipelines"


class PipelineStages(InsightlyStream):
    primary_key = "STAGE_ID"

    def path(self, **kwargs) -> str:
        return "PipelineStages"


class ProjectCategories(InsightlyStream):
    primary_key = "CATEGORY_ID"

    def path(self, **kwargs) -> str:
        return "ProjectCategories"


class Relationships(InsightlyStream):
    primary_key = "RELATIONSHIP_ID"

    def path(self, **kwargs) -> str:
        return "Relationships"


class Tags(InsightlyStream):
    primary_key = "TAG_NAME"

    def path(self, **kwargs) -> str:
        return "Tags"


class TaskCategories(InsightlyStream):
    primary_key = "CATEGORY_ID"

    def path(self, **kwargs) -> str:
        return "TaskCategories"


class TeamMembers(InsightlyStream):
    primary_key = "MEMBER_USER_ID"

    def path(self, **kwargs) -> str:
        return "TeamMembers"


class Teams(InsightlyStream):
    primary_key = "TEAM_ID"

    def path(self, **kwargs) -> str:
        return "Teams"


class IncrementalInsightlyStream(InsightlyStream, ABC):
    """Insighlty incremental stream using `updated_after_utc` filter"""

    cursor_field = "DATE_UPDATED_UTC"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

        start_datetime = pendulum.parse(self.start_date)
        if stream_state.get(self.cursor_field):
            start_datetime_raw = stream_state[self.cursor_field]
            if isinstance(start_datetime_raw, datetime):
                start_datetime = start_datetime_raw
            else:
                start_datetime = pendulum.parse(stream_state[self.cursor_field])

        # Add one second to avoid duplicate records and ensure greater than
        params.update({"updated_after_utc": (start_datetime + timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")})
        return params

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        record_time = pendulum.parse(latest_record[self.cursor_field])
        current_state = current_stream_state.get(self.cursor_field)
        if current_state:
            current_state = current_state if isinstance(current_state, datetime) else pendulum.parse(current_state)

        current_stream_state[self.cursor_field] = max(record_time, current_state) if current_state else record_time
        return current_stream_state


class Contacts(IncrementalInsightlyStream):
    primary_key = "CONTACT_ID"

    def path(self, **kwargs) -> str:
        return "Contacts/Search"


class Events(IncrementalInsightlyStream):
    primary_key = "EVENT_ID"

    def path(self, **kwargs) -> str:
        return "Events/Search"


class KnowledgeArticleCategories(IncrementalInsightlyStream):
    primary_key = "CATEGORY_ID"

    def path(self, **kwargs) -> str:
        return "KnowledgeArticleCategory/Search"


class KnowledgeArticleFolders(IncrementalInsightlyStream):
    primary_key = "FOLDER_ID"

    def path(self, **kwargs) -> str:
        return "KnowledgeArticleFolder/Search"


class KnowledgeArticles(IncrementalInsightlyStream):
    primary_key = "ARTICLE_ID"

    def path(self, **kwargs) -> str:
        return "KnowledgeArticle/Search"


class Leads(IncrementalInsightlyStream):
    primary_key = "LEAD_ID"

    def path(self, **kwargs) -> str:
        return "Leads/Search"


class Milestones(IncrementalInsightlyStream):
    primary_key = "MILESTONE_ID"

    def path(self, **kwargs) -> str:
        return "Milestones/Search"


class Notes(IncrementalInsightlyStream):
    primary_key = "NOTE_ID"

    def path(self, **kwargs) -> str:
        return "Notes/Search"


class Opportunities(IncrementalInsightlyStream):
    primary_key = "OPPORTUNITY_ID"

    def path(self, **kwargs) -> str:
        return "Opportunities/Search"


class OpportunityProducts(IncrementalInsightlyStream):
    primary_key = "OPPORTUNITY_ITEM_ID"

    def path(self, **kwargs) -> str:
        return "OpportunityLineItem/Search"


class Organisations(IncrementalInsightlyStream):
    primary_key = "ORGANISATION_ID"

    def path(self, **kwargs) -> str:
        return "Organisations/Search"


class PricebookEntries(IncrementalInsightlyStream):
    primary_key = "PRICEBOOK_ENTRY_ID"

    def path(self, **kwargs) -> str:
        return "PricebookEntry/Search"


class Pricebooks(IncrementalInsightlyStream):
    primary_key = "PRICEBOOK_ID"

    def path(self, **kwargs) -> str:
        return "Pricebook/Search"


class Products(IncrementalInsightlyStream):
    primary_key = "PRODUCT_ID"

    def path(self, **kwargs) -> str:
        return "Product/Search"


class Projects(IncrementalInsightlyStream):
    primary_key = "PROJECT_ID"

    def path(self, **kwargs) -> str:
        return "Projects/Search"


class Prospects(IncrementalInsightlyStream):
    primary_key = "PROSPECT_ID"

    def path(self, **kwargs) -> str:
        return "Prospect/Search"


class QuoteProducts(IncrementalInsightlyStream):
    primary_key = "QUOTATION_ITEM_ID"

    def path(self, **kwargs) -> str:
        return "QuotationLineItem/Search"


class Quotes(IncrementalInsightlyStream):
    primary_key = "QUOTE_ID"

    def path(self, **kwargs) -> str:
        return "Quotation/Search"


class Tasks(IncrementalInsightlyStream):
    primary_key = "TASK_ID"

    def path(self, **kwargs) -> str:
        return "Tasks/Search"


class Tickets(IncrementalInsightlyStream):
    primary_key = "TICKET_ID"

    def path(self, **kwargs) -> str:
        return "Ticket/Search"


class Users(IncrementalInsightlyStream):
    primary_key = "USER_ID"

    def path(self, **kwargs) -> str:
        return "Users/Search"


# Source
class SourceInsightly(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            token = config.get("token")
            response = requests.get(f"{BASE_URL}Instance", auth=(token, ""))
            response.raise_for_status()

            result = response.json()
            logger.info(result)

            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """

        auth = BasicHttpAuthenticator(username=config.get("token"), password="")
        return [
            ActivitySets(authenticator=auth, **config),
            Contacts(authenticator=auth, **config),
            Countries(authenticator=auth, **config),
            Currencies(authenticator=auth, **config),
            Emails(authenticator=auth, **config),
            Events(authenticator=auth, **config),
            KnowledgeArticleCategories(authenticator=auth, **config),
            KnowledgeArticleFolders(authenticator=auth, **config),
            KnowledgeArticles(authenticator=auth, **config),
            LeadSources(authenticator=auth, **config),
            LeadStatuses(authenticator=auth, **config),
            Leads(authenticator=auth, **config),
            Milestones(authenticator=auth, **config),
            Notes(authenticator=auth, **config),
            Opportunities(authenticator=auth, **config),
            OpportunityCategories(authenticator=auth, **config),
            OpportunityProducts(authenticator=auth, **config),
            OpportunityStateReasons(authenticator=auth, **config),
            Organisations(authenticator=auth, **config),
            PipelineStages(authenticator=auth, **config),
            Pipelines(authenticator=auth, **config),
            PricebookEntries(authenticator=auth, **config),
            Pricebooks(authenticator=auth, **config),
            Products(authenticator=auth, **config),
            ProjectCategories(authenticator=auth, **config),
            Projects(authenticator=auth, **config),
            Prospects(authenticator=auth, **config),
            QuoteProducts(authenticator=auth, **config),
            Quotes(authenticator=auth, **config),
            Relationships(authenticator=auth, **config),
            Tags(authenticator=auth, **config),
            TaskCategories(authenticator=auth, **config),
            Tasks(authenticator=auth, **config),
            TeamMembers(authenticator=auth, **config),
            Teams(authenticator=auth, **config),
            Tickets(authenticator=auth, **config),
            Users(authenticator=auth, **config),
        ]
