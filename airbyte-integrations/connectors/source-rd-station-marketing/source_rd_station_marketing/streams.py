#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from datetime import date
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.sources.streams.http import HttpStream


class RDStationMarketingStream(HttpStream, ABC):
    data_field = None
    extra_params = {}
    page = 1
    page_size_limit = 125
    primary_key = None
    url_base = "https://api.rd.services"

    def __init__(self, authenticator, start_date=None, **kwargs):
        super().__init__(authenticator=authenticator, **kwargs)
        self._start_date = start_date

    def path(self, **kwargs) -> str:
        class_name = self.__class__.__name__
        return f"/platform/{class_name[0].lower()}{class_name[1:]}"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self.data_field:
            json_response = response.json().get(self.data_field)
        else:
            json_response = response.json()
        if json_response:
            self.page = self.page + 1
            return {"next_page": self.page}
        else:
            return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"page_size": self.page_size_limit, "page": self.page}
        if next_page_token:
            params = {"page_size": self.page_size_limit, "page": next_page_token["next_page"]}
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if self.data_field:
            records = response.json().get(self.data_field)
        else:
            records = response.json()
        yield from records


class IncrementalRDStationMarketingStream(RDStationMarketingStream):
    def path(self, **kwargs) -> str:
        return f"/platform/analytics/{self.data_field}"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        start_date = self._start_date

        if start_date and stream_state.get(self.cursor_field):
            start_date = max(pendulum.parse(stream_state[self.cursor_field]), start_date)

        params = {}
        params.update(
            {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": date.today().strftime("%Y-%m-%d"),
            }
        )

        params.update(self.extra_params)
        return params

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}


class AnalyticsConversions(IncrementalRDStationMarketingStream):
    """
    API docs: https://developers.rdstation.com/reference/get_platform-analytics-conversions
    """

    data_field = "conversions"
    cursor_field = "asset_updated_at"
    primary_key = "asset_id"


class AnalyticsEmails(IncrementalRDStationMarketingStream):
    """
    API docs: https://developers.rdstation.com/reference/get_platform-analytics-emails
    """

    data_field = "emails"
    cursor_field = "send_at"
    primary_key = "campaign_id"


class AnalyticsFunnel(IncrementalRDStationMarketingStream):
    """
    API docs: https://developers.rdstation.com/reference/get_platform-analytics-funnel
    """

    data_field = "funnel"
    cursor_field = "reference_day"
    primary_key = "reference_day"


class AnalyticsWorkflowEmailsStatistics(IncrementalRDStationMarketingStream):
    """
    API docs: https://developers.rdstation.com/reference/get_platform-analytics-workflow-emails
    """

    data_field = "workflow_email_statistics"
    cursor_field = "updated_at"
    primary_key = "workflow_id"

    def path(self, **kwargs) -> str:
        return "/platform/analytics/workflow_emails_statistics"


class Emails(RDStationMarketingStream):
    """
    API docs: https://developers.rdstation.com/reference/get_platform-emails
    """

    data_field = "items"
    primary_key = "id"


class Embeddables(RDStationMarketingStream):
    """
    API docs: https://developers.rdstation.com/reference/get_platform-embeddables
    """

    primary_key = "id"


class Fields(RDStationMarketingStream):
    """
    API docs: https://developers.rdstation.com/reference/get_platform-contacts-fields
    """

    data_field = "fields"
    primary_key = "uuid"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(self, **kwargs) -> str:
        return "/platform/contacts/fields"


class LandingPages(RDStationMarketingStream):
    """
    API docs: https://developers.rdstation.com/reference/get_platform-landing-pages
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "/platform/landing_pages"


class Popups(RDStationMarketingStream):
    """
    API docs: https://developers.rdstation.com/reference/get_platform-popups
    """

    primary_key = "id"


class Segmentations(RDStationMarketingStream):
    """
    API docs: https://developers.rdstation.com/reference/get_platform-segmentations
    """

    data_field = "segmentations"
    primary_key = "id"


class Workflows(RDStationMarketingStream):
    """
    API docs: https://developers.rdstation.com/reference/get_platform-workflows
    """

    data_field = "workflows"
    primary_key = "id"
