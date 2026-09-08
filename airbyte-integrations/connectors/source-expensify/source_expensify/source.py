# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import csv
import json
import pkgutil
import time
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any, Iterable, List, Mapping, Optional, Tuple

import requests

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, UserDefinedBackoffException
from airbyte_cdk.sources.streams.http.rate_limiting import default_backoff_handler, user_defined_backoff_handler
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


EXPENSIFY_URL = "https://integrations.expensify.com/Integration-Server/ExpensifyIntegrations"
RAW_CSV_DEBUG_DIR = Path("/tmp/source_expensify_debug")
REPORTS_EXPORT_TEMPLATE_PATH = "templates/reports_export_template.ftl"

MAX_RETRIES = 5
RETRY_FACTOR = 5
RATE_LIMIT_BACKOFF_SECONDS = 10.0


class PolicyNotFoundError(Exception):
    """Raised when the Expensify policy doesn't exist (HTTP 410)."""


class CredentialsInvalidError(Exception):
    """Raised when the Expensify credentials are invalid (HTTP 401)."""


class RateLimitExceededError(Exception):
    """Raised when the Expensify API rate limit is exceeded (HTTP 429)."""


def _load_reports_export_template() -> str:
    """Load the Expensify export template used to shape the combined report CSV output."""
    package = __name__.split(".")[0]
    template_bytes = pkgutil.get_data(package, REPORTS_EXPORT_TEMPLATE_PATH)
    if template_bytes is None:
        raise FileNotFoundError(f"Unable to find {REPORTS_EXPORT_TEMPLATE_PATH} in the package.")
    return template_bytes.decode("utf-8")


def _map_response_code_to_exception(response_code: int) -> None:
    """Map an Expensify response code to an exception."""
    if response_code == requests.codes.gone:
        # Expensify returns 410 if the policy doesn't exist
        raise PolicyNotFoundError(f"Expensify policy not found.")
    elif response_code == requests.codes.unauthorized:
        # Expensify returns 401 if the credentials are invalid
        raise CredentialsInvalidError(f"Expensify credentials are invalid.")
    elif response_code == requests.codes.too_many_requests:
        # Expensify returns 429 if the API rate limit is exceeded
        raise RateLimitExceededError(f"Expensify API rate limit exceeded.")
    elif response_code >= 500:
        # 5xx codes indicate a problem on Expensify's side that may be transient.
        raise AirbyteTracedException(
            internal_message=f"Expensify returned server error response code {response_code}.",
            message=f"Expensify API request failed with a server error (code {response_code}). This is likely transient, please try again later.",
            failure_type=FailureType.transient_error,
        )
    elif response_code >= requests.codes.bad_request:
        # Other 4xx codes typically won't succeed on retry, so surface them to Airbyte as a config error.
        raise AirbyteTracedException(
            internal_message=f"Expensify returned client error response code {response_code}.",
            message=f"Expensify API request failed with client error (code {response_code}). Please verify your configuration.",
            failure_type=FailureType.config_error,
        )


@user_defined_backoff_handler(max_tries=MAX_RETRIES)
@default_backoff_handler(max_tries=MAX_RETRIES, factor=RETRY_FACTOR)
def _send_request(payload: Mapping[str, Any]) -> requests.Response:
    """
    Send the actual HTTP request to the Expensify Integration Server, retrying it using the
    Airbyte CDK's standard backoff handlers: HTTP 429 responses back off for a fixed duration,
    transient 5xx/connection errors are retried with exponential backoff, and all other 4xx
    errors are treated as permanent failures and raised immediately without retrying.
    """
    response = requests.post(EXPENSIFY_URL, data=payload, timeout=60)
    if response.status_code == requests.codes.too_many_requests:
        raise UserDefinedBackoffException(backoff=RATE_LIMIT_BACKOFF_SECONDS, request=response.request, response=response)
    if response.status_code >= 500:
        raise DefaultBackoffException(request=response.request, response=response)
    response.raise_for_status()
    return response


def _post_job_description(job_description: Mapping[str, Any], template: Optional[str] = None) -> requests.Response:
    """
    Send a requestJobDescription to the Expensify Integration Server.

    Expensify requires the `requestJobDescription` form field to be a JSON-encoded string.

    `template` (when provided) must be sent as its own top-level form field, sibling to
    `requestJobDescription`.
    """
    payload = {"requestJobDescription": json.dumps(job_description)}
    if template is not None:
        payload["template"] = template
    response = _send_request(payload)

    # Expensify returns HTTP 200 even for some error conditions, with a JSON error body
    # like {"responseMessage": "...", "responseCode": 500}. Detect and surface those.
    stripped = response.text.strip()
    if stripped.startswith("{") and '"responseCode"' in stripped:
        try:
            error_body = json.loads(stripped)
        except json.JSONDecodeError:
            error_body = None
        if error_body and "responseCode" in error_body:
            response_code = error_body.get("responseCode")
            _map_response_code_to_exception(response_code)

    return response


class ExpensifyReports(Stream):
    # Airbyte uses this to know what column uniquely identifies a row
    primary_key = "reportID"

    def __init__(self, name: str, partner_user_id: str, partner_user_secret: str, start_date: str, end_date: str, **kwargs):
        super().__init__(**kwargs)
        self._name = name
        self.partner_user_id = partner_user_id
        self.partner_user_secret = partner_user_secret
        self.start_date = start_date
        self.end_date = end_date

    @property
    def name(self) -> str:
        return self._name

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        self.logger.info(f"Reading records from Expensify for {self.name}")
        # Step 1: Trigger the Export Job
        file_name = self._trigger_export()
        self.logger.info(f"Triggered Expensify export for file {file_name}.")

        # Step 2: Download the CSV
        csv_data = self._download_file(file_name)
        self.logger.info(f"Downloaded Expensify export ({len(csv_data)} bytes) for file {file_name}.")

        # Step 3: Parse CSV in memory and yield rows to Airbyte
        reader = csv.DictReader(StringIO(csv_data))
        record_count = 0
        for row in reader:
            # Airbyte takes these yielded dicts, validates them against your schema,
            # and streams them to the destination connector
            record_count += 1
            yield row
        self.logger.info(f"Parsed {record_count} record(s) from Expensify export.")

    def _trigger_export(self) -> str:
        job_description = {
            "type": "file",
            "credentials": {
                "partnerUserID": self.partner_user_id,
                "partnerUserSecret": self.partner_user_secret,
            },
            "onReceive": {"immediateResponse": ["returnRandomFileName"]},
            "inputSettings": {
                "type": "combinedReportData",
                "filters": {
                    "startDate": self.start_date,
                    "endDate": self.end_date,
                },
                "reportState": "REIMBURSED",
            },
            "outputSettings": {"fileExtension": "csv"},
        }
        response = _post_job_description(job_description, template=_load_reports_export_template())
        return response.text.strip()

    def _download_file(self, file_name: str) -> str:
        job_description = {
            "type": "download",
            "credentials": {"partnerUserID": self.partner_user_id, "partnerUserSecret": self.partner_user_secret},
            "fileName": file_name,
            "fileSystem": "integrationServer",
        }
        response = _post_job_description(job_description)
        return response.text


class SourceExpensify(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, Any]:
        # Validate that the provided credentials actually work
        try:
            # Request a non-existent policy to ensure credentials are valid
            job_description = {
                "type": "get",
                "credentials": {
                    "partnerUserID": config["partner_user_id"],
                    "partnerUserSecret": config["partner_user_secret"],
                },
                "inputSettings": {"type": "policy", "fields": ["reportFields"], "policyIDList": ["abc"]},
            }
            response = _post_job_description(job_description)
            # Ensure the response is valid JSON
            response.json()
            return True, None
        except PolicyNotFoundError:
            # Expensify returns 410 if the policy doesn't exist
            logger.info("Credentials are valid.")
            return True, None
        except CredentialsInvalidError:
            # Expensify returns 401 if the credentials are invalid
            logger.info("Credentials are invalid.")
            return False, None
        except Exception as e:
            logger.info(f"Other issue connecting to Expensify: {e}")
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # Pass the credentials from the Airbyte UI into your stream
        return [
            ExpensifyReports(
                name="reports",
                partner_user_id=config["partner_user_id"],
                partner_user_secret=config["partner_user_secret"],
                start_date=config["start_date"],
                end_date=config["end_date"],
            )
        ]
