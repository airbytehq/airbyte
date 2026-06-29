#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import logging
from typing import Any, List, Mapping, Tuple

import requests

from airbyte_cdk.models import AirbyteCatalog, AirbyteStream, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import (
    Absentees,
    Availabilities,
    Departments,
    Employees,
    EmployeesReport,
    EmployeeTimeDistribution,
    ScheduleDetailReport,
    Shifts,
    TimesheetDetailReport,
    Users,
)


logger = logging.getLogger("airbyte")


# Source
class SourceShiftbase(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, Any]:
        """
        Sends a request to absentees endpoint to check if the connection is successful for all accounts.
        """
        try:
            accounts = config.get("accounts", [])
            if not accounts:
                return False, "No accounts configured."

            for account in accounts:
                access_token = account.get("access_token")
                account_name = account.get("account_name")

                if not access_token or not account_name:
                    return False, f"Missing access_token or account_name for account configuration."

                endpoint = "https://api.shiftbase.com/api/absentees"
                headers = {"Authorization": f"API {access_token}", "Content-Type": "application/json", "Accept": "application/json"}

                response = requests.get(url=endpoint, headers=headers)

                if response.status_code != 200:
                    return (
                        False,
                        f"Failed to connect to account {account_name} with status code: {response.status_code}, response: {response.text}",
                    )

            return True, None

        except Exception as e:
            logger.error(f"An exception occurred: {str(e)}")
            return False, str(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        accounts = config.get("accounts", [])
        start_date = config.get("start_date")

        logger.info("Starting stream initialization")

        # Initialize base streams with all accounts
        departments = Departments(accounts=accounts, start_date=start_date)

        # Get department IDs for all accounts
        department_ids = []
        try:
            department_ids = self.extract_department_ids(departments)
            logger.info(f"Found {len(department_ids)} departments")
            if not department_ids:
                logger.warning("No departments found. Employee-related streams may be empty.")
        except Exception as e:
            logger.error(f"Failed to fetch departments during stream init: {e}")
            # Continue with empty list to allow discovery to succeed

        # Initialize all streams regardless of data availability
        employees = Employees(accounts=accounts, start_date=start_date, department_ids=department_ids)

        # Get employee IDs for all accounts
        employee_ids = []
        if department_ids:
            try:
                employee_ids = self.extract_employee_ids(employees)
                logger.info(f"Found {len(employee_ids)} employees")
                if not employee_ids:
                    logger.warning("No employees found. Employee time distribution stream will be empty.")
                else:
                    logger.info(f"Employees available.")
            except Exception as e:
                logger.error(f"Failed to fetch employees during stream init: {e}")
                # Continue with empty list

        streams = [
            Departments(accounts=accounts, start_date=start_date),
            Employees(accounts=accounts, start_date=start_date, department_ids=department_ids),
            Absentees(accounts=accounts, start_date=start_date),
            EmployeeTimeDistribution(accounts=accounts, start_date=start_date, employee_ids=employee_ids),
            Availabilities(accounts=accounts, start_date=start_date),
            Shifts(accounts=accounts, start_date=start_date),
            Users(accounts=accounts, start_date=start_date),
            EmployeesReport(accounts=accounts, start_date=start_date),
            TimesheetDetailReport(accounts=accounts, start_date=start_date),
            ScheduleDetailReport(accounts=accounts, start_date=start_date),
        ]

        logger.info("=== Stream Configuration ===")
        for stream in streams:
            logger.info(f"\nStream: {stream.name}")
            logger.info(f"  Primary Key: {stream.primary_key}")
            logger.info(f"  Sync Modes: {stream.supported_sync_modes}")
            if hasattr(stream, "cursor_field") and stream.cursor_field:
                logger.info(f"  Cursor Field: {stream.cursor_field}")
        logger.info("=========================")

        try:
            logger.info("Starting schema discovery")
            for stream in streams:
                logger.info(f"Getting schema for {stream.name}")
                schema = stream.get_json_schema()
                logger.info(f"Schema loaded for {stream.name}: {list(schema.keys())}")
        except Exception as e:
            logger.error(f"Error during schema discovery: {e}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error details: {str(e)}")
            raise

        logger.info("Returning streams")
        return streams

    def extract_department_ids(self, departments_stream):
        """
        Extract department IDs from the departments stream.
        Each department record is nested under a 'Department' key.
        """
        departments_list = []
        try:
            logger.debug("Starting department extraction")
            for department in departments_stream.read_records(sync_mode=None):
                if isinstance(department, dict):
                    dept_data = {"id": department.get("id"), "account_name": department.get("account_name")}
                    departments_list.append(dept_data)
                else:
                    logger.warning(f"Unexpected department format: {department}")
        except Exception as e:
            logger.error(f"Error extracting department IDs: {e}")
            logger.exception("Full traceback:")

        logger.debug(f"Extracted departments")
        return departments_list

    def extract_employee_ids(self, employees_stream):
        """
        Extract employee IDs from the employees stream.
        """
        employee_ids = []
        try:
            logger.debug("Starting employee extraction")
            for employee in employees_stream.read_records(sync_mode=None):
                if not isinstance(employee, dict):
                    logger.warning(f"Skipping non-dictionary employee record: {employee}")
                    continue

                # Try to get the ID from the employee record
                employee_id = employee.get("id")
                if employee_id:
                    employee_ids.append(employee_id)
                else:
                    logger.warning(f"No ID found in employee record: {employee}")

        except Exception as e:
            logger.error(f"Error extracting employee IDs: {e}")
            logger.exception("Full traceback:")

        logger.info(f"Total extracted employee IDs: {len(employee_ids)}")
        if employee_ids:
            logger.info(f"Sample of extracted employee IDs: {employee_ids[:5]}")
        return employee_ids

    def discover(self, logger, config) -> AirbyteCatalog:
        """
        Returns an AirbyteCatalog representing the available streams.
        """
        streams = self.streams(config)

        logger.info("Starting catalog discovery")
        streams_list = []

        for stream in streams:
            logger.info(f"Processing stream: {stream.name}")
            try:
                schema = stream.get_json_schema()
                logger.info(f"Schema loaded for {stream.name}")

                # The sync modes are already SyncMode enums, so we can use them directly
                airbyte_stream = AirbyteStream(
                    name=stream.name,
                    json_schema=schema,
                    supported_sync_modes=stream.supported_sync_modes,  # No conversion needed
                    source_defined_cursor=stream.source_defined_cursor,
                    default_cursor_field=[stream.cursor_field] if hasattr(stream, "cursor_field") and stream.cursor_field else None,
                    source_defined_primary_key=[[stream.primary_key]] if hasattr(stream, "primary_key") and stream.primary_key else None,
                )

                # Log the stream configuration
                logger.info(f"Stream configuration for {stream.name}:")
                logger.info(f"  - Sync modes: {[mode.value for mode in stream.supported_sync_modes]}")  # Convert to string only for logging
                logger.info(f"  - Cursor: {airbyte_stream.default_cursor_field}")
                logger.info(f"  - Primary key: {airbyte_stream.source_defined_primary_key}")
                logger.info(f"  - Schema: {json.dumps(schema)[:200]}...")

                streams_list.append(airbyte_stream)
                logger.info(f"Added {stream.name} to catalog")

            except Exception as e:
                logger.error(f"Error processing stream {stream.name}: {e}")
                logger.error(f"Error type: {type(e)}")
                logger.error(f"Error details: {str(e)}")
                raise

        catalog = AirbyteCatalog(streams=streams_list)

        # Log the final catalog
        logger.info("Final catalog:")
        logger.info(
            json.dumps(
                {
                    "streams": [
                        {
                            "name": s.name,
                            "supported_sync_modes": [mode.value for mode in s.supported_sync_modes],  # Convert to string for logging
                            "source_defined_cursor": s.source_defined_cursor,
                            "default_cursor_field": s.default_cursor_field,
                            "source_defined_primary_key": s.source_defined_primary_key,
                        }
                        for s in catalog.streams
                    ]
                },
                indent=2,
            )
        )

        return catalog
