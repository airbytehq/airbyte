#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator
from airbyte_cdk.models import SyncMode

POLLING_IN_SECONDS = 60
class DFAReportingStream(HttpStream):
    """
    Base stream for DFA Reporting API.
    """
    url_base = "https://dfareporting.googleapis.com"
    
    def __init__(self, profile_id: str, authenticator: Oauth2Authenticator, **kwargs):
        super().__init__(authenticator=authenticator)
        self.profile_id = profile_id
    
    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, *kwargs) -> Iterable[Mapping]:
        # Implement response parsing
        yield response.json()

class CreateReport(DFAReportingStream):
    """
    Stream for creating a report in DFA Reporting.
    """
    primary_key = "id"
    http_method = "POST"

    def path(self, **kwargs) -> str:
        return f"/dfareporting/v4/userprofiles/{self.profile_id}/reports"
    
    def request_body_json(self, **kwargs) -> Mapping[str, Any]:
        today = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
        two_years_ago = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=730)).strftime('%Y-%m-%d')
        return {
            "type": "STANDARD",
            "name": f"report_{today}",
            "criteria": {
                "dateRange": {
                    "kind": "dfareporting#dateRange",
                    "endDate": today,
                    "startDate": two_years_ago
                },
                "dimensions": [
                    {"kind": "dfareporting#sortedDimension", "name": "activity"},
                    {"kind": "dfareporting#sortedDimension", "name": "ad"},
                    {"kind": "dfareporting#sortedDimension", "name": "advertiser"},
                    {"kind": "dfareporting#sortedDimension", "name": "advertiserID"},
                    {"kind": "dfareporting#sortedDimension", "name": "campaign"},
                    {"kind": "dfareporting#sortedDimension", "name": "campaignEndDate"},
                    {"kind": "dfareporting#sortedDimension", "name": "campaignStartDate"},
                    {"kind": "dfareporting#sortedDimension", "name": "date"},
                    {"kind": "dfareporting#sortedDimension", "name": "dmaRegion"}
                ],
                "metricNames": [
                    "clicks",
                    "costPerClick",
                    "totalConversionsRevenue",
                    "costPerRevenue",
                    "impressions",
                    "mediaCost",
                    "effectiveCpm",
                    "revenuePerClick",
                    "revenuePerThousandImpressions",
                    "socialTotalEngagements"
                ]
            }
        }
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping[str, Any]]:
        print(response.json())
        yield response.json()

class RunReport(DFAReportingStream):
    """
    Stream for running a created report.
    """
    primary_key = "id"
    http_method = "POST"
    parent = CreateReport

    def __init__(self, profile_id: str, authenticator: Oauth2Authenticator, **kwargs):
        super().__init__(profile_id, authenticator, **kwargs)
        self.parent_stream = CreateReport(profile_id, authenticator)

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        print(stream_slice)
        report_id = stream_slice.get("report_id") if stream_slice else None
        if not report_id:
            raise ValueError("No report ID found in stream slice")
        return f"/dfareporting/v4/userprofiles/{self.profile_id}/reports/{report_id}/run"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        create_report_record = next(self.parent_stream.read_records(sync_mode=SyncMode.full_refresh))
        yield {"report_id": create_report_record["id"]}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping[str, Any]]:
        yield response.json()

class ReportData(DFAReportingStream):
    """
    TODO: Change class name to match the table/data source this stream corresponds to.
    """

    # TODO: Fill in the cursor_field. Required.
    cursor_field = "start_date"

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = "employee_id"

    def path(self, **kwargs) -> str:
        """
        TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/employees then this should
        return "single". Required.
        """
        return "employees"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        """
        TODO: Optionally override this method to define this stream's slices. If slicing is not needed, delete this method.

        Slices control when state is saved. Specifically, state is saved after a slice has been fully read.
        This is useful if the API offers reads by groups or filters, and can be paired with the state object to make reads efficient. See the "concepts"
        section of the docs for more information.

        The function is called before reading any records in a stream. It returns an Iterable of dicts, each containing the
        necessary data to craft a request for a slice. The stream state is usually referenced to determine what slices need to be created.
        This means that data in a slice is usually closely related to a stream's cursor_field and stream_state.

        An HTTP request is made for each returned slice. The same slice can be accessed in the path, request_params and request_header functions to help
        craft that specific request.

        For example, if https://example-api.com/v1/employees offers a date query params that returns data for that particular day, one way to implement
        this would be to consult the stream state object for the last synced date, then return a slice containing each date from the last synced date
        till now. The request_params function would then grab the date from the stream_slice and make it part of the request by injecting it into
        the date query param.
        """
        raise NotImplementedError("Implement stream slices or delete this method!")


# Source
class SourceCampaignManager(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        TODO: Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # TODO remove the authenticator if not required.
        auth = TokenAuthenticator(token="api_key")  # Oauth2Authenticator is also available if you need oauth support
        return [Customers(authenticator=auth), Employees(authenticator=auth)]
