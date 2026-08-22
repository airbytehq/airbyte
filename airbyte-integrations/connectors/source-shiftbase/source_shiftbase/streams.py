#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import logging
import os
import time
from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from requests.auth import AuthBase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException


logger = logging.getLogger("airbyte")


class ShiftbaseStream(HttpStream, ABC):
    """
    API Docs: https://developer.shiftbase.com/docs/core/59f133358c1fd-shiftbase-api
    """

    url_base = "https://api.shiftbase.com/api/"
    # Maximum number of retries for recoverable errors
    max_retries = 5
    # Default retry delay if Retry-After header is not present
    default_retry_delay = 30
    # Add supported sync modes to base class
    supported_sync_modes = [SyncMode.full_refresh]
    source_defined_cursor = False

    def as_airbyte_stream(self) -> Stream:
        """
        Override to ensure proper stream conversion with sync modes
        """
        stream = super().as_airbyte_stream()
        stream.supported_sync_modes = [SyncMode(mode) for mode in self.supported_sync_modes]
        stream.source_defined_cursor = self.source_defined_cursor
        if hasattr(self, "cursor_field"):
            stream.default_cursor_field = [self.cursor_field]
        return stream

    def __init__(
        self,
        accounts: List[dict],
        start_date: str,
        authenticator: Optional[AuthBase] = None,
    ):
        super().__init__(authenticator=authenticator)
        self.accounts = accounts
        self.start_date = start_date
        self._rate_limit_remaining = 180  # Default rate limit
        self._rate_limit_reset = None

        # Initialize account iteration
        self.current_account_index = 0
        self.current_account = self.accounts[0]
        self.access_token = self.current_account["access_token"]

    def should_retry(self, response: requests.Response) -> bool:
        """
        Override to add custom retry logic for specific HTTP status codes.
        """
        if response.status_code == 429:  # Rate limit exceeded
            return True
        elif response.status_code in [500, 502, 503, 504]:  # Server errors
            return True
        # Don't retry for other status codes (including 401 Unauthorized)
        return False

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        Returns backoff time in seconds based on response headers or status code.
        """
        # Update rate limit info from headers
        self._update_rate_limits(response)

        # Check for Retry-After header first
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            return float(retry_after)

        # Handle rate limit cases
        if response.status_code == 429:
            if self._rate_limit_reset:
                # Calculate wait time until rate limit reset
                wait_time = self._rate_limit_reset - time.time()
                return max(wait_time, 1)  # Ensure we wait at least 1 second
            return self.default_retry_delay

        # Exponential backoff for server errors
        if response.status_code in [500, 502, 503, 504]:
            return self.default_retry_delay

        return None

    def _update_rate_limits(self, response: requests.Response) -> None:
        """
        Updates internal rate limit tracking based on response headers.
        """
        try:
            if "X-RateLimit-Remaining" in response.headers:
                self._rate_limit_remaining = int(response.headers["X-RateLimit-Remaining"])

            if "X-RateLimit-Reset" in response.headers:
                self._rate_limit_reset = int(response.headers["X-RateLimit-Reset"])

            # Log rate limit information
            if self._rate_limit_remaining < 20:  # Warning threshold
                logger.warning(
                    f"Rate limit running low. Remaining: {self._rate_limit_remaining}, "
                    f"Reset at: {datetime.fromtimestamp(self._rate_limit_reset).isoformat() if self._rate_limit_reset else 'unknown'}"
                )
        except (ValueError, TypeError) as e:
            logger.warning(f"Error parsing rate limit headers: {e}")

    def request_headers(
        self,
        stream_state: Mapping[str, Any] | None,
        stream_slice: Mapping[str, Any] | None = None,
        next_page_token: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any]:
        return {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"API {self.access_token}"}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            "min_date": self.start_date  # If not present the current day will be used.
        }

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Override to add general error handling around the record reading process.
        """
        try:
            yield from super().read_records(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise DefaultBackoffException(request=e.request, response=e.response)
        except Exception as e:
            logger.error(f"Unexpected error while reading records: {e}")
            raise

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Handle account iteration. Returns None when all accounts are processed.
        """
        if self.current_account_index + 1 < len(self.accounts):
            self.current_account_index += 1
            self.current_account = self.accounts[self.current_account_index]
            self.access_token = self.current_account["access_token"]
            return {"account_index": self.current_account_index}
        return None


class Employees(ShiftbaseStream):
    """
    API Docs: https://developer.shiftbase.com/docs/core/75d0181c0add8-list-employees-in-department
    """

    primary_key = "id"
    # Inherits supported_sync_modes from ShiftbaseStream

    def __init__(
        self,
        accounts: List[dict],
        start_date: str,
        department_ids: List[dict],
        authenticator: Optional[AuthBase] = None,
    ):
        super().__init__(accounts, start_date, authenticator)
        self.department_ids = department_ids
        self.current_department_index = 0
        self.current_department = self.department_ids[0] if self.department_ids else None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if not self.current_department:
            logger.warning("No current department available")
            return "hr/departments/0/employeeList"  # This will return empty result
        return f"hr/departments/{self.current_department['id']}/employeeList"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Parse employees response.
        """
        try:
            response_json = response.json()

            if response.status_code != 200:
                logger.error(f"Error response from employees endpoint: {response_json}")
                return []

            data = response_json.get("data")
            if not data:
                logger.warning("No data found in response")
                return []

            for record in data:
                if not isinstance(record, dict):
                    logger.warning(f"Skipping non-dictionary record: {record}")
                    continue

                # Add required fields to the record
                record["department_id"] = self.current_department["id"]
                record["account_name"] = self.current_account["account_name"]

                # Rename fields to match schema
                if "teamId" in record:
                    record["team_id"] = record.pop("teamId")

                yield record

        except Exception as e:
            logger.error(f"Error parsing employees response: {e}")
            logger.error(f"Response content: {response.text}")
            raise

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Handle both department and account iteration
        """
        if not self.department_ids:
            return super().next_page_token(response)

        if self.current_department_index + 1 < len(self.department_ids):
            self.current_department_index += 1
            self.current_department = self.department_ids[self.current_department_index]
            # If we're switching to a department from a different account, update the access token
            if self.current_department["account_name"] != self.current_account["account_name"]:
                for account in self.accounts:
                    if account["account_name"] == self.current_department["account_name"]:
                        self.current_account = account
                        self.access_token = account["access_token"]
                        break
            return {"department_index": self.current_department_index}

        # If we've processed all departments, try next account
        self.current_department_index = 0  # Reset department index
        if self.department_ids:  # Reset current department if we have departments
            self.current_department = self.department_ids[0]
        return super().next_page_token(response)

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Override to handle case where no departments exist
        """
        if not self.department_ids:
            logger.warning("No departments available to fetch employees from")
            return []

        yield from super().read_records(*args, **kwargs)


class EmployeeTimeDistribution(ShiftbaseStream):
    """
    API Docs: https://developer.shiftbase.com/docs/core/9ceb4dce3acb8-list-employee-time-distribution
    """

    primary_key = "employeeId"
    # Inherits supported_sync_modes from ShiftbaseStream

    def __init__(
        self,
        accounts: List[dict],
        start_date: str,
        employee_ids: List,
        authenticator: Optional[AuthBase] = None,
    ):
        super().__init__(accounts, start_date, authenticator)
        # Employee handling
        self.employee_ids = [eid for eid in employee_ids if eid is not None]  # Filter out None values
        self.current_employee_index = 0
        self.current_employee = None
        if self.employee_ids:
            self.current_employee = self.employee_ids[0]

        # Year handling
        try:
            self.start_year = datetime.strptime(self.start_date, "%Y-%m-%d").year
            self.current_year = datetime.now().year
            self.current_year_index = self.start_year
        except ValueError as e:
            logger.error(f"Error parsing start date {self.start_date}: {e}")
            self.start_year = datetime.now().year
            self.current_year = self.start_year
            self.current_year_index = self.start_year

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        The API expects a year parameter for time distribution
        """
        return {"year": self.current_year_index}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Handle year, employee, and account iteration
        """
        if not self.employee_ids:
            return None

        # First try next year for current employee
        if self.current_year_index < self.current_year:
            self.current_year_index += 1
            return {"year": self.current_year_index}

        # If we've processed all years, try next employee
        if self.current_employee_index + 1 < len(self.employee_ids):
            self.current_employee_index += 1
            self.current_employee = self.employee_ids[self.current_employee_index]
            self.current_year_index = self.start_year  # Reset year for new employee
            return {"employee_index": self.current_employee_index}

        # If we've processed all employees, try next account
        next_account_token = super().next_page_token(response)
        if next_account_token:
            # Reset indices for new account
            self.current_employee_index = 0
            self.current_employee = self.employee_ids[0]
            self.current_year_index = self.start_year
            return next_account_token

        logger.info("Finished processing all accounts, employees, and years")
        return None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if not self.current_employee:
            logger.warning("No current employee ID available")
            return "employees/0/time_distribution"  # This will return empty result
        return f"employees/{self.current_employee}/time_distribution"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Parse time distribution response.
        """
        try:
            response_json = response.json()

            if response.status_code != 200:
                logger.error(f"Error response from time distribution endpoint: {response_json}")
                return []

            data = response_json.get("data", {})
            if data:
                data.update(
                    {
                        "account_name": self.current_account["account_name"],
                        "employee_id": self.current_employee,
                        "year": self.current_year_index,
                    }
                )
                yield data

        except Exception as e:
            logger.error(f"Error parsing time distribution response: {e}")
            logger.error(f"Response content: {response.text}")
            raise

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Override to handle case where no employee IDs exist
        """
        if not self.employee_ids:
            logger.warning("No employee IDs available for time distribution")
            return []

        yield from super().read_records(*args, **kwargs)


# Basic incremental stream
class IncrementalShiftbaseStream(ShiftbaseStream, ABC):
    """
    Base class for implementing incremental streams for Shiftbase connector.
    """

    state_checkpoint_interval = 100
    cursor_field = None
    # Add incremental sync mode for incremental streams
    supported_sync_modes = [SyncMode.full_refresh, SyncMode.incremental]
    source_defined_cursor = True

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object.
        State is maintained per account.
        """
        current_stream_state = current_stream_state or {}
        account_name = latest_record["account_name"]

        # Initialize account state if not present
        if account_name not in current_stream_state:
            current_stream_state[account_name] = {self.cursor_field: self.start_date}

        latest_record_value = latest_record.get(self.cursor_field, self.start_date)
        current_account_value = current_stream_state[account_name].get(self.cursor_field, self.start_date)

        current_stream_state[account_name][self.cursor_field] = max(latest_record_value, current_account_value)
        return current_stream_state

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Extends request params with state filter if available.
        Uses per-account state for filtering.
        """
        params = super().request_params(stream_state, stream_slice, next_page_token)

        # Only include state filter if we have stream state for current account
        if stream_state and self.current_account["account_name"] in stream_state:
            account_state = stream_state[self.current_account["account_name"]]
            params["min_date"] = account_state.get(self.cursor_field, self.start_date)

        return params


class Departments(ShiftbaseStream):
    """
    API Docs: https://developer.shiftbase.com/docs/core/510254d159b47-list-departments
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "departments"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Parse departments response.
        """
        try:
            response_json = response.json()
            logger.debug(f"Departments response: {response_json}")

            if response.status_code != 200:
                logger.error(f"Error response from departments endpoint: {response_json}")
                return []

            data = response_json.get("data", [])
            if not data:
                logger.warning(f"No departments found in response: {response_json}")
                return []

            for record in data:
                department = record.get("Department", record)
                if department:
                    # Add account_name to the department data
                    department["account_name"] = self.current_account["account_name"]
                    yield department
                else:
                    logger.warning(f"Could not extract department data from record: {record}")

        except Exception as e:
            logger.error(f"Error parsing departments response: {e}")
            logger.error(f"Response content: {response.text}")
            raise


class Absentees(IncrementalShiftbaseStream):
    """
    API Docs: https://developer.shiftbase.com/docs/core/2e1fba402f9bb-list-absentees
    """

    primary_key = "id"
    cursor_field = "updated"
    # Inherits supported_sync_modes from IncrementalShiftbaseStream

    def path(self, **kwargs) -> str:
        return "absentees"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Parse absentees response.
        """
        response_json = response.json()
        logger.debug(f"Absentees response: {response_json}")  # Debug logging

        data = response_json.get("data", [])
        for record in data:
            absentee = record.get("Absentee", {})
            if absentee:
                # Add account_name to the absentee data
                absentee["account_name"] = self.current_account["account_name"]
                yield absentee


class Availabilities(IncrementalShiftbaseStream):
    """
    API Docs: https://developer.shiftbase.com/docs/core/0b8b4f51ba73a-list-availabilities
    """

    primary_key = "id"
    cursor_field = "date"
    # Inherits supported_sync_modes from IncrementalShiftbaseStream

    def path(self, **kwargs) -> str:
        return "availabilities"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Parse absentees response with error handling.
        """
        try:
            # Check response status
            if response.status_code != 200:
                logger.error(f"Error response from availabilities endpoint: {response_json}")
                return []

            response_json = response.json()
            data = response_json.get("data", [])

            # Process records
            for record in data:
                try:
                    availability = record.get("Availability", {})
                    if not availability:
                        logger.warning(f"No Availability data found in record: {record}")
                        continue

                    # Add account_name to the availability data
                    availability["account_name"] = self.current_account["account_name"]
                    yield availability

                except Exception as record_error:
                    logger.error(f"Error processing individual record: {record_error}")
                    logger.debug(f"Problematic record: {record}")
                    continue  # Skip this record but continue processing others

        except requests.exceptions.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response content: {response.text}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error parsing availabilities response: {e}")
            logger.error(f"Response content: {response.text}")
            raise


class Shifts(ShiftbaseStream):
    """
    API Docs: https://developer.shiftbase.com/docs/core/c8dbe25e28719-list-shifts
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "shifts"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Parse shifts response.
        """
        try:
            response_json = response.json()
            if response.status_code != 200:
                logger.error(f"Error response from shifts endpoint: {response_json}")
                return []

            data = response_json.get("data", [])

            for record in data:
                # Handle potentially wrapped record
                shift = record.get("Shift", record)
                if shift:
                    shift["account_name"] = self.current_account["account_name"]
                    yield shift
                else:
                    logger.warning(f"Could not extract shift data from record: {record}")

        except Exception as e:
            logger.error(f"Error parsing shifts response: {e}")
            logger.error(f"Response content: {response.text}")
            raise


class Users(ShiftbaseStream):
    """
    API Docs: https://developer.shiftbase.com/docs/core/7b22ead2360d9-list-users
    Inherits from ShiftbaseStream which handles the authentication and base URL.
    Incremental sync is not supported for this stream due to modified/updated request parameter not being available.
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "users"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Parse users response.
        """
        try:
            response_json = response.json()
            if response.status_code != 200:
                logger.error(f"Error response from users endpoint: {response_json}")
                return []

            data = response_json.get("data", [])

            for record in data:
                user_record = record.get("User")
                if user_record:
                    user_record["account_name"] = self.current_account["account_name"]
                    yield user_record
                else:
                    logger.warning(f"Could not extract user data from record: {record}")

        except Exception as e:
            logger.error(f"Error parsing users response: {e}")
            logger.error(f"Response content: {response.text}")
            raise

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Overwrite request_params to remove min_date parameter. Not available for this stream.
        """
        return None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Does not support pagination.
        """
        return None


class EmployeesReport(ShiftbaseStream):
    """
    API Docs: https://developer.shiftbase.com/docs/core/4d05f64e94419-employees-report
    Inherits from ShiftbaseStream which handles the authentication and base URL.
    Incremental sync is not supported for this stream due to modified/updated request parameter not being available.
    """

    primary_key = "userId"
    http_method = "POST"

    def __init__(
        self,
        accounts: List[dict],
        start_date: str,
        authenticator: Optional[AuthBase] = None,
    ):
        super().__init__(accounts, start_date, authenticator)

    def path(self, **kwargs) -> str:
        return "reports/users"

    def request_body_json(self, **kwargs) -> Optional[Mapping[str, Any]]:
        return {"export": "json", "from": self.start_date}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Parse employees report response.
        """
        try:
            response_json = response.json()
            if response.status_code != 200:
                logger.error(f"Error response from employees report endpoint: {response_json}")
                return []

            for record in response_json:
                if record:
                    record["account_name"] = self.current_account["account_name"]
                    yield record
                else:
                    logger.warning(f"Could not extract data from Employees Report record: {record}")

        except Exception as e:
            logger.error(f"Error parsing employees report response: {e}")
            logger.error(f"Response content: {response.text}")
            raise

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Overwrite request_params to remove min_date parameter. Not available for this stream.
        """
        return None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Does not support pagination.
        """
        return None


class TimesheetDetailReport(ShiftbaseStream):
    """
    API Docs: https://developer.shiftbase.com/docs/core/5612d41bb72b1-timesheet-detail-report
    Inherits from ShiftbaseStream which handles the authentication and base URL.
    Incremental sync is not supported for this stream due to modified/updated request parameter not being available.
    """

    primary_key = "timesheetId"
    http_method = "POST"

    def __init__(
        self,
        accounts: List[dict],
        start_date: str,
        authenticator: Optional[AuthBase] = None,
    ):
        super().__init__(accounts, start_date, authenticator)
        self.current_date = self.start_date

    def path(self, **kwargs) -> str:
        return "reports/timesheet_detail"

    def request_body_json(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping[str, Any]]:
        date_to_use = self.current_date
        if next_page_token and "current_date" in next_page_token:
            date_to_use = next_page_token["current_date"]

        return {"export": "json", "from": date_to_use, "to": date_to_use}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Parse timesheet detail report response.
        """
        try:
            response_json = response.json()
            if response.status_code != 200:
                logger.error(f"Error response from timesheet detail report endpoint: {response_json}")
                return []

            for record in response_json:
                if record:
                    record["account_name"] = self.current_account["account_name"]
                    yield record
                else:
                    logger.warning(f"Could not extract data from Timesheet Detail Report record: {record}")

        except Exception as e:
            logger.error(f"Error parsing timesheet detail report response: {e}")
            logger.error(f"Response content: {response.text}")
            raise

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Overwrite request_params to remove min_date parameter. Not available for this stream.
        """
        return None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Iterate day-by-day and then switch to next account.
        """
        # Current date being processed
        current_date_dt = datetime.strptime(self.current_date, "%Y-%m-%d")
        next_date_dt = current_date_dt + timedelta(days=1)
        today_dt = datetime.now()

        if next_date_dt <= today_dt:
            self.current_date = next_date_dt.strftime("%Y-%m-%d")
            return {"current_date": self.current_date, "account_index": self.current_account_index}

        # Else: Dates for current account exhausted. Move to next account.
        if self.current_account_index + 1 < len(self.accounts):
            self.current_account_index += 1
            self.current_account = self.accounts[self.current_account_index]
            self.access_token = self.current_account["access_token"]
            self.current_date = self.start_date
            return {"current_date": self.current_date, "account_index": self.current_account_index}

        return None


class ScheduleDetailReport(ShiftbaseStream):
    """
    API Docs: https://developer.shiftbase.com/docs/core/122ab05b95b82-schedule-detail-report
    Inherits from ShiftbaseStream which handles the authentication and base URL.
    Incremental sync is not supported for this stream due to modified/updated request parameter not being available.
    """

    primary_key = "userId"
    http_method = "POST"

    def __init__(
        self,
        accounts: List[dict],
        start_date: str,
        authenticator: Optional[AuthBase] = None,
    ):
        super().__init__(accounts, start_date, authenticator)
        self.current_date = self.start_date

    def path(self, **kwargs) -> str:
        return "reports/schedule_detail"

    def request_body_json(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Optional[Mapping[str, Any]]:
        date_to_use = self.current_date
        if next_page_token and "current_date" in next_page_token:
            date_to_use = next_page_token["current_date"]

        return {"export": "json", "from": date_to_use, "to": date_to_use}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Parse schedule detail report response.
        """
        try:
            response_json = response.json()
            if response.status_code != 200:
                logger.error(f"Error response from schedule detail report endpoint: {response_json}")
                return []

            for record in response_json:
                if record:
                    record["account_name"] = self.current_account["account_name"]
                    yield record
                else:
                    logger.warning(f"Could not extract data from Schedule Detail Report record: {record}")

        except Exception as e:
            logger.error(f"Error parsing schedule detail report response: {e}")
            logger.error(f"Response content: {response.text}")
            raise

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Overwrite request_params to remove min_date parameter. Not available for this stream.
        """
        return None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Iterate day-by-day and then switch to next account.
        """
        # Current date being processed
        current_date_dt = datetime.strptime(self.current_date, "%Y-%m-%d")
        next_date_dt = current_date_dt + timedelta(days=1)
        today_dt = datetime.now()

        if next_date_dt <= today_dt:
            self.current_date = next_date_dt.strftime("%Y-%m-%d")
            return {"current_date": self.current_date, "account_index": self.current_account_index}

        # Else: Dates for current account exhausted. Move to next account.
        if self.current_account_index + 1 < len(self.accounts):
            self.current_account_index += 1
            self.current_account = self.accounts[self.current_account_index]
            self.access_token = self.current_account["access_token"]
            self.current_date = self.start_date
            return {"current_date": self.current_date, "account_index": self.current_account_index}

        return None
