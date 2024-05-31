#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from datetime import datetime, timedelta

import requests
import json
import time
import random
import tempfile
import os
import csv
import pytz
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream

# Basic full refresh stream
class PhilzUberEatsStream(HttpStream, ABC):
    
    url_base = 'https://ubereats-reports-zkwdzsbzhq-wl.a.run.app/api/v1/GenerateReport'
    report_type = None
    first_run = True
    old_cursor_value = None
    new_cursor_value = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        self.logger.info("PhilzUberEatsStream.next_page_token")
        return None

# Basic incremental stream
class IncrementalPhilzUberEatsStream(PhilzUberEatsStream, ABC):
    http_method = "POST"
    start_date_from_config = "2023-12-31"
    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        return ["check_order_date"]
    
    def request_body_json(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> Optional[Mapping]:
        self.logger.info("IncrementalPhilzUberEatsStream.request_body_json")
        
        # Get the current date in Los Angeles
        tz = pytz.timezone('America/Los_Angeles')
        now = datetime.now(tz)
        current_date = now.strftime("%Y-%m-%d")

        # Common request body logic here, including start date handling
        if self.first_run:
            body = {
                "report_type": "NONE",  # Use NONE for first run
                "start_date": current_date,
            }
        else:
            # Get the start_date from the uber-eats-reports service.
            self.logger.info(f"Getting start date for: {self.report_type}.")
            get_start_date_url = f"https://ubereats-reports-zkwdzsbzhq-wl.a.run.app/api/v1/StartDate?report_type={self.report_type}"
            get_start_date_response = requests.get(get_start_date_url, headers=self.authenticator.get_auth_header())
            start_date_str = get_start_date_response.json()['start_date']
            # Set old_cursor_value to start date to be compared later.
            self.old_cursor_value = start_date_str
            self.logger.info(f'Start date for {self.report_type} : {start_date_str}.')

            # Parse the start_date string into a datetime object
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')

            # Subtract 7 days from the start_date
            new_start_date = start_date - timedelta(days=7)

            # Format the new_start_date back into a string
            new_start_date_str = new_start_date.strftime('%Y-%m-%d')

            self.logger.info(f'New start date (7 days earlier) for {self.report_type} : {new_start_date_str}.')

            # Use the new_start_date_str in your request body
            body = {
                "report_type": self.report_type,  # Use the subclass-defined report type
                "start_date": new_start_date_str,
            }

        self.logger.info(f"Request body: {json.dumps(body, indent=2)}")
        return body


    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        # Retrieve the cursor value from the latest record, defaulting to the start_date_from_config if not present
        latest_record_cursor_value = latest_record.get(self.cursor_field, self.start_date_from_config)
        
        # Retrieve the current cursor value from the state, with the same default
        current_state_cursor_value = current_stream_state.get(self.cursor_field, self.start_date_from_config)
        
        # Determine the new cursor value based on the max of the latest record and current state
        try:
            new_cursor_value = max(latest_record_cursor_value, current_state_cursor_value)
        except TypeError as e:
            # Log in case of a comparison error, e.g., if the cursor fields are not directly comparable
            self.logger.error(f"Error comparing cursor values: {e}")
            raise

        # Return the updated state
        self.new_cursor_value = new_cursor_value
        return {self.cursor_field: new_cursor_value}
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        self.logger.info("IncrementalPhilzUberEatsStream.parse_response")
        if self.first_run:
            self.logger.info("This is the first run of parse_response.")
            self.first_run = False 
            return
        else:
            self.logger.info("This is a subsequent run of parse_response.")

        response_data = response.json()

        # Check if the response data is a list of dictionaries with 'workflow_id' as a key
        if isinstance(response_data, list) and all('workflow_id' in d for d in response_data):
            workflow_ids = [d['workflow_id'] for d in response_data]
            self.logger.info(f"Create report request completed. Workflow IDs: {workflow_ids}.")
        else:
            self.logger.error("Response data is not in the expected format or 'workflow_id' key is missing")
            raise ValueError("Response data is not in the expected format or 'workflow_id' key is missing")

        for workflow_id in workflow_ids:
            self.logger.info(f"Processing Workflow ID: {workflow_id}.")
            get_report_url = f"https://ubereats-reports-zkwdzsbzhq-wl.a.run.app/api/v1/ReportDownloadUrl?workflow_id={workflow_id}"
            delay = 1
            max_delay = 60  # maximum delay of 1 minute
            time_start = time.time()

            # Initial request
            get_report_response = requests.get(get_report_url, headers=self.authenticator.get_auth_header())
            self.logger.info(f"Initial request made for report: {workflow_id}.")

            # Exponential backoff until report is ready or 10 minutes passed
            while not get_report_response.ok or ('report_status' in get_report_response.json() and get_report_response.json()['report_status'] != 'SUCCEEDED' and time.time() - time_start < 600): 
                self.logger.info(f"Waiting for report, current delay: {delay} seconds.")
                time.sleep(delay)
                delay = min(delay * 1.5, max_delay) + random.uniform(0, 0.5)  # increase delay by a factor of 1.5 and add up to 0.5 seconds of jitter
                get_report_response = requests.get(get_report_url, headers=self.authenticator.get_auth_header())
                self.logger.info("Made another request for report.")

            # Check if report generation succeeded
            if get_report_response.json().get('report_status') != 'SUCCEEDED':
                msg = f'Report for Workflow ID {workflow_id} not ready in 10 minutes. Terminating process.'
                self.logger.error(msg)
                raise TimeoutError(msg)  # Raise an exception to indicate failure
            else:
                self.logger.info(f"Report for Workflow ID {workflow_id} is ready.")


            # Get the direct link to the CSV file
            download_url = get_report_response.json()['download_url']
            self.logger.info(f'Report ready for download. URL: {download_url}.')

            # Download and process the CSV file
            report_download_response = requests.get(download_url, headers=self.authenticator.get_auth_header())

            # Generate a unique filename using the current workflow ID
            unique_filename = f'report_{workflow_id}.csv'

            with tempfile.TemporaryDirectory() as temp_dir:
                csv_file_path = os.path.join(temp_dir, unique_filename)
                with open(csv_file_path, 'wb') as csv_file:
                    csv_file.write(report_download_response.content)
                
                self.logger.info(f'Report downloaded. CSV file written to {csv_file_path}.')

                with open(csv_file_path, 'r', encoding='utf_8') as f:
                    self.logger.info(f'Counting rows in {unique_filename}.')
                    csv_reader = csv.reader(f)
                    row_count = sum(1 for row in csv_reader) - 1  # Subtract 1 for the header row

                    self.logger.info(f'Total rows in {unique_filename}: {row_count}')

                # Read and process the CSV file

                with open(csv_file_path, 'r', encoding='utf_8') as f:
                    self.logger.info(f'Reading rows from {unique_filename}.')
                    csv_reader = csv.DictReader(f)

                    for row in csv_reader:
                        # self.logger.info(f"Processing row: {json.dumps(row)}")
                        yield row
        
        # Store the new cursor value in StartDate by report_type
        self.logger.info(f"Old cursor date: {self.old_cursor_value}, New cursor date: {self.new_cursor_value}")
        # Convert date strings to datetime objects
        old_cursor_date = datetime.strptime(self.old_cursor_value, '%Y-%m-%d')
        new_cursor_date = datetime.strptime(self.new_cursor_value, '%Y-%m-%d')
        # Check if the new cursor date is greater than the old cursor date
        if new_cursor_date > old_cursor_date:
            self.logger.info(f"New cursor date {self.new_cursor_value} is greater than old cursor date {self.old_cursor_value}. Proceeding with POST request.")
            post_url = "https://ubereats-reports-zkwdzsbzhq-wl.a.run.app/api/v1/StartDate"  # Change to your actual endpoint
            body = {
                "report_type": self.report_type,  # Use the subclass-defined report type
                "start_date": self.new_cursor_value
            }
            post_response = requests.post(post_url, json=body, headers=self.authenticator.get_auth_header())
            
            if post_response.status_code == 200:
                self.logger.info(f'Successfully posted data for {self.report_type}. Status code: {post_response.status_code}')
            else:
                self.logger.error(f'Failed to post data for {self.report_type}. Status code: {post_response.status_code}, Response: {post_response.text}')
        else:
            self.logger.info(f"No update needed. The new cursor {self.new_cursor_value} is not after the old cursor {self.old_cursor_value}.")


class OrderDetails(IncrementalPhilzUberEatsStream):

    cursor_field = "check_order_date"
    primary_key = "generated_key"
    report_type = "ORDERS_AND_ITEMS_REPORT"

    def path(self, **kwargs) -> str:
        # set path to "" to override default behaviour
        # this will allow us to call url_base = 'https://ubereats-reports-zkwdzsbzhq-wl.a.run.app/api/v1/GenerateReport' without /api/v1/???
        return ""

# Source
class SourcePhilzUberEats(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [OrderDetails()]
