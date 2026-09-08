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

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream


EXPENSIFY_URL = "https://integrations.expensify.com/Integration-Server/ExpensifyIntegrations"
RAW_CSV_DEBUG_DIR = Path("/tmp/source_expensify_debug")
REPORTS_EXPORT_TEMPLATE_PATH = "templates/reports_export_template.ftl"


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


def _map_response_code_to_exception(response_code: int) -> Optional[Exception]:
    """Map an Expensify response code to an exception."""
    if response_code == 410:
        # Expensify returns 410 if the policy doesn't exist
        raise PolicyNotFoundError(f"Expensify policy not found.")
    elif response_code == 401:
        # Expensify returns 401 if the credentials are invalid
        raise CredentialsInvalidError(f"Expensify credentials are invalid.")
    elif response_code == 429:
        # Expensify returns 429 if the API rate limit is exceeded
        raise RateLimitExceededError(f"Expensify API rate limit exceeded.")


def _post_job_description(job_description: Mapping[str, Any], template: Optional[str] = None) -> requests.Response:
    """
    Send a requestJobDescription to the Expensify Integration Server.

    Expensify requires the `requestJobDescription` form field to be a JSON-encoded
    string, not a native Python dict - requests would otherwise form-encode it using
    Python's repr() (single quotes, True/False), which Expensify rejects as invalid JSON.

    `template` (when provided) must be sent as its own top-level form field, sibling to
    `requestJobDescription`, not nested inside it - Expensify rejects nested templates
    with "No Template Submitted".
    """
    payload = {"requestJobDescription": json.dumps(job_description)}
    if template is not None:
        payload["template"] = template
    response = requests.post(EXPENSIFY_URL, data=payload, timeout=60)
    response.raise_for_status()

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
            # and streams them to Postgres
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
        # Tell Expensify exactly what columns to output
        response = _post_job_description(job_description, template=_load_reports_export_template())
        return response.text.strip()

    def _download_file(self, file_name: str) -> str:
        # Re-request the download now that we know it's ready
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
