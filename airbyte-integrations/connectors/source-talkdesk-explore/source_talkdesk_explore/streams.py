#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from abc import abstractmethod
from datetime import datetime
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream

logger = AirbyteLogger()


class GenerateReportStream(HttpStream):
    """This stream is specifically for generating the report in Talkdesk.
    - HTTP method: POST
    - Returns: ID of the generated report

    """

    primary_key = None

    def __init__(self, base_path, start_date, timezone, **kwargs):
        super().__init__(**kwargs)
        self.base_path = base_path
        self.start_date = start_date
        self.timezone = timezone

    @property
    def url_base(self) -> str:
        return "https://api.talkdeskapp.com/data/"

    @property
    def http_method(self) -> str:
        return "POST"

    def path(self, **kwargs) -> str:
        return self.base_path

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        logger.info(f"Generating {self.base_path} report from '{self.start_date}' to '{now}'")
        return {
            "format": "json",
            "timespan": {
                "from": self.start_date,
                "to": now,
                "timezone": self.timezone,
            },
        }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        id_obj = {"id": response_json["job"]["id"]}
        logger.info(f"Generated report with ID '{id_obj['id']}'")

        return [id_obj]


class ReadReportStream(HttpStream):
    primary_key = None

    def __init__(self, start_date, timezone, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.timezone = timezone

    @property
    def url_base(self) -> str:
        return "https://api.talkdeskapp.com/data/"

    def path(self, **kwargs) -> str:
        latest_state = kwargs.get("stream_state").get(self.cursor_field, None)

        if not latest_state:
            latest_state = self.start_date

        # Check and set latest_state to necessary date-time format
        try:
            datetime.strptime(latest_state, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            try:
                datetime.strptime(latest_state, "%Y-%m-%d %H:%M:%S")
                latest_state = latest_state.replace(" ", "T")
            except ValueError:
                logger.error("stream_state is in unhandled date-time format. Required format: %Y-%m-%dT%H:%M:%S")

        generate_report = GenerateReportStream(
            base_path=self.base_path, start_date=latest_state, timezone=self.timezone, authenticator=self.authenticator
        )
        report_id = next(generate_report.read_records(SyncMode.full_refresh))

        return self.base_path + f"/{report_id['id']}"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def should_retry(self, response: requests.Response) -> bool:
        """
        Retry conditions:
        1. By default, back off on the following HTTP response statuses:
         - 429 (Too Many Requests) indicating rate limiting
         - 500s to handle transient server errors
         - Unexpected but transient exceptions (connection timeout, DNS resolution failed, etc..) are retried by default.
        2. When the report is requested but is not ready to be fetched:
         - In that case, the response will have the following format:
         ```
         {"job": {"id": "369f88a5-d5a3-42c6-a135-8aec4215553e", "name": "Calls",
         "created_at": "2022-01-13T10:17:15", "status": "processing", "type": "calls", "format": "json", ...}}
         ```
         The retry function will be looking for a response in this format with 'status' different than 'completed'.
         Please refer to the docs to read more about executing a report: https://docs.talkdesk.com/docs/executing-report.

        """
        if response.status_code == 429 or 500 <= response.status_code < 600:
            return True
        else:
            response_obj = response.json()
            try:
                report_status = response_obj["job"]["status"]
                if report_status != "completed":
                    logger.info("Requested report is in uncompleted status. Waiting for it to be completed...")
                    return True
                else:
                    return False
            except KeyError:
                # Report failures
                if response.status_code in [400, 401, 403]:
                    logger.error(f"Report returned an invalid response: {json.dumps(response_obj)}")
                    raise ValueError("Requested report is in invalid/failed state.")
                # TODO: implement handling of other response types here.
                return False

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        try:
            yield from response_json["entries"]
        except KeyError:
            logger.warn("No entries found in requested report. Setting it to null.")
            yield from []


class IncrementalReadReportStream(ReadReportStream):
    """
    Incremental append for the ReadReportStream. This class introduces the 'cursor_field'
    and 'get_updated_state' methods.

    """

    @property
    @abstractmethod
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, so any incremental stream must extend this class
        and define a cursor field.
        """
        pass

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_state = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(self.cursor_field) or latest_state
        return {self.cursor_field: max(latest_state, current_state)}


class Calls(IncrementalReadReportStream):
    @property
    def primary_key(self) -> str:
        return "call_id"

    @property
    def base_path(self) -> str:
        return "reports/calls/jobs"

    @property
    def cursor_field(self) -> str:
        return "end_at"


class UserStatus(IncrementalReadReportStream):
    @property
    def primary_key(self) -> str:
        return "user_id"

    @property
    def base_path(self) -> str:
        return "reports/user_status/jobs"

    @property
    def cursor_field(self) -> str:
        return "status_end_at"


class StudioFlowExecution(IncrementalReadReportStream):
    @property
    def primary_key(self) -> str:
        return "flow_id"

    @property
    def base_path(self) -> str:
        return "reports/studio_flow_execution/jobs"

    @property
    def cursor_field(self) -> str:
        return "studio_flow_executions_aggregated.flow_execution_finished_time"


class Contacts(IncrementalReadReportStream):
    @property
    def primary_key(self) -> str:
        return "contact_id"

    @property
    def base_path(self) -> str:
        return "reports/contacts/jobs"

    @property
    def cursor_field(self) -> str:
        return "finished_at"


class RingAttempts(IncrementalReadReportStream):
    @property
    def primary_key(self) -> str:
        return "ring_attempt_id"

    @property
    def base_path(self) -> str:
        return "reports/ring_attempts/jobs"

    @property
    def cursor_field(self) -> str:
        return "ring_finished_at_time"
