from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from datetime import datetime, timedelta
import pytz
import time
import tempfile
import os
import csv
import random

# Main Source Class for UberEats
class SourceUberEats(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            return True, None
        except Exception as e:
            return False, e
    
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(token=config['api_key'])
        return [
            OrderDetails(authenticator=auth, config=config),
        ]




# Base Stream for UberEats
class UberEatsStream(HttpStream, ABC):
    url_base = 'https://ubereats-reports-zkwdzsbzhq-wl.a.run.app/api/v1/GenerateReport'  # Updated URL
    

    def __init__(self, config: Mapping[str, any], *args, **kwargs):
        self.start_date_from_config = config.get('start_date')
        super().__init__(*args, **kwargs)

# Incremental Stream for fetching data incrementally from UberEats
class IncrementalUberEatsStream(UberEatsStream):    
    http_method = "POST"
    cursor_field = "ACTIVE_DATE"  # Default cursor field

    def path(self, **kwargs) -> str:
        return ""
    
    # Method to get updated state based on latest record and current stream state
    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:        
        latest_record_cursor_value = latest_record.get(self.cursor_field, self.start_date_from_config)
        current_state_cursor_value = current_stream_state.get(self.cursor_field, self.start_date_from_config)
        new_cursor_value = max(latest_record_cursor_value, current_state_cursor_value)
        return {self.cursor_field: new_cursor_value}

    # Method to get request body for API call
    def request_body_json(
    self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Optional[Mapping]:        
        start_date = self.start_date_from_config        
        if stream_state.get(self.cursor_field):
            start_date = stream_state.get(self.cursor_field)

        # Formatting start_date
        if len(start_date) > 10:
            start_date = start_date[:10]

        
        # Adjusting start_date for ensuring capture of all changes
        temp_date = datetime.strptime(start_date, "%Y-%m-%d")
        start_date = temp_date.astimezone(pytz.utc).strftime("%Y-%m-%d")

        self.logger.info(f"Start date: {start_date}")
        request_json = { 
            "start_date": start_date,
        }

        self.logger.info(f"Sending request: {request_json}")
        return request_json
    
    # Method to get the next page token, none in this case as pagination is not handled here
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None    

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
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

            get_report_response = requests.get(get_report_url, headers=self.authenticator.get_auth_header())

            # Initial request
            get_report_response = requests.get(get_report_url, headers=self.authenticator.get_auth_header())
            self.logger.info("Initial request made for report.")

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
                        yield row

# Specific stream classes for different report types
class OrderDetails(IncrementalUberEatsStream):    
    primary_key = "ORDER_ID"

