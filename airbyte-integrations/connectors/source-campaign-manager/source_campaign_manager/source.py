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
    primary_key = None
    parent = RunReport

    def __init__(self, profile_id: str, authenticator: Oauth2Authenticator, **kwargs):
        super().__init__(profile_id, authenticator, **kwargs)
        self.parent_stream = RunReport(profile_id, authenticator)

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        report_id = stream_slice.get("report_id") if stream_slice else None
        file_id = stream_slice.get("file_id") if stream_slice else None
        if not report_id or not file_id:
            raise ValueError("Missing report_id or file_id in stream slice")
        return f"/dfareporting/v4/reports/{report_id}/files/{file_id}"
    
    def request_params(self, **kwargs) -> Mapping[str, Any]:
        return {"alt": "media"}
    
    def stream_slices(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Optional[Mapping[str, Any]]]:
        for slice_run_report in self.parent_stream.stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state):
            for record_run_report in self.parent_stream.read_records(sync_mode=sync_mode, stream_slice=slice_run_report):
                yield {
                    "report_id": slice_run_report["report_id"],
                    "file_id": record_run_report["id"]
                }

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == 404:
            return True
        return super().should_retry(response)
    
    def backoff_time(self, response: requests.Response) -> Optional[float]:
        if isinstance(response, Exception):
            self.logger.warning(f"Back off due to {type(response)}.")
            return POLLING_IN_SECONDS
        elif response.status_code == 404:
            self.logger.warning("Report file not ready yet.")
            return POLLING_IN_SECONDS
        return super().backoff_time(response)
    
    def parse_response(self, response, stream_state = None, stream_slice = None, *kwargs):
        print("response hereee")
        csv_string = StringIO(response.text)

        # Skip lines until we find "Report Fields"
        for line in csv_string:
            if "Report Fields" in line:
                break
        headers = next(csv.reader(csv_string))

        # Now we can use DictReader with the correct headers
        csv_reader = csv.DictReader(csv_string, fieldnames=headers)
        
        for row in csv_reader:
            print(row)
            yield row

class SourceCampaignManager(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            authenticator = Oauth2Authenticator(
                token_refresh_endpoint="https://oauth2.googleapis.com/token",
                client_id=config["client_id"],
                client_secret=config["client_secret"],
                refresh_token=config["refresh_token"],
            )
            create_report = CreateReport(config["profile_id"], authenticator)
            next(create_report.read_records(sync_mode=SyncMode.full_refresh))
            return True, None
        except Exception as e:
            return False, f"Unable to connect to DFA Reporting API: {str(e)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = Oauth2Authenticator(
            token_refresh_endpoint="https://oauth2.googleapis.com/token",
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=config["refresh_token"],
        )
        return [
            # CreateReport(config["profile_id"], authenticator),
            # RunReport(config["profile_id"], authenticator),
            ReportData(config["profile_id"], authenticator),
        ]