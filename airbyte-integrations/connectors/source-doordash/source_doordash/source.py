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
import zipfile
import os
import csv


class DoordashStream(HttpStream, ABC):
    url_base = 'https://openapi.doordash.com/dataexchange/v1/reports'

    def __init__(self, config: Mapping[str, any], *args, **kwargs):
        self.start_date_from_config = config.get('start_date')
        super().__init__(*args, **kwargs)

# Basic incremental stream
class IncrementalDoordashStream(DoordashStream):    
    http_method = "POST"

    # Value to pass to DoorDash. Default to order detail fields. Subclass should override.
    report_type = "ORDER_DETAIL"
    cursor_field = "ACTIVE_DATE"

    def path(self, **kwargs) -> str:
        return ""
    
    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:        
        latest_record_cursor_value = latest_record.get(self.cursor_field, self.start_date_from_config)
        current_state_cursor_value = current_stream_state.get(self.cursor_field, self.start_date_from_config)
        new_cursor_value = max(latest_record_cursor_value, current_state_cursor_value)
        return {self.cursor_field: new_cursor_value}

    def request_body_json(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None,
        store_ids: List[int] = []
    ) -> Optional[Mapping]:        
        start_date = self.start_date_from_config        
        if stream_state.get(self.cursor_field):
            start_date = stream_state.get(self.cursor_field)
        
        # Remove the time portion of it if it's present.
        if len(start_date) > 10:
            start_date = start_date[:10]

        self.logger.info(f"Start date: {start_date}")

        # To capture all the changes on the DoorDash side, we would always go back 7 days. The dedup process
        # on the destination side will handle all the clean up.
        temp_date = datetime.strptime(start_date, "%Y-%m-%d")
        temp_date = temp_date - timedelta(days=7)
        start_date = temp_date.astimezone(pytz.utc).strftime("%Y-%m-%d")

        end_date = datetime.now().astimezone(pytz.utc).strftime("%Y-%m-%d")

        request_json = { 
            "store_ids": store_ids,
            "start_date": start_date,
            "end_date": end_date,
            "report_type": self.report_type
        }
        self.logger.info(f"Sending request: {request_json}")
        return request_json
    
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None    

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # Initial create report request would provide a report ID.
        report_id = response.json()['report_id']
        self.logger.info(f"Create report request completed. Report ID: {report_id}.")
        get_report_url = f"{self.url_base}/{report_id}/reportlink"

        # Check to see if the report is ready for download with an exponential backoff. Loop until it's ready. Also 
        # provide a way out of the loop if it takes more than 10 minutes.
        delay = 1
        time_start = time.time()
        time_current = time_start
        get_report_response = requests.get(get_report_url, headers=self.authenticator.get_auth_header())
        while not get_report_response.ok or (get_report_response.json()['report_status'] != 'SUCCEEDED' and time_current - time_start < 600): 
            time.sleep(delay)
            delay += delay
            get_report_response = requests.get(get_report_url, headers=self.authenticator.get_auth_header())
            time_current = time.time()

        # Terminate further processing if we exit the loop due to timeout.
        if get_report_response.json()['report_status'] != 'SUCCEEDED':
            msg = 'DoorDash does not provide a report download URL in 10 minutes. Terminating.'
            self.logger.error(msg)
            raise Exception(msg)

        # Download the report as a temp file.        
        report_link = get_report_response.json()['report_link']
        self.logger.info(f'Report ready for download. URL: {report_link}.')
        report_download_response = requests.get(report_link, headers=self.authenticator.get_auth_header())
        with tempfile.TemporaryDirectory() as temp_dir:
            with tempfile.TemporaryFile(dir=temp_dir, suffix='.zip') as report_zip_file:
                report_zip_file.write(report_download_response.content)
                report_zip_file.flush()
                self.logger.info(f'Report download. Zip file written to {report_zip_file.name}.')

                # Unzip the zip file.
                with zipfile.ZipFile(report_zip_file, 'r') as zip_obj:
                    file_list = zip_obj.namelist()
                    for file_name in file_list:
                        csv_dest = os.path.join(temp_dir, file_name)
                        self.logger.info(f'Extracting file {csv_dest}.')
                        zip_obj.extract(file_name, path=temp_dir)

                        # Load the extracted CSV.
                        with open(csv_dest, 'r', encoding='utf_8') as f:
                            self.logger.info(f'Reading rows from {csv_dest}.')
                            csv_reader = csv.DictReader(f)

                            # Yield return each row as a json record.
                            for row in csv_reader:
                                yield row


class OrderDetails(IncrementalDoordashStream):    
    primary_key = "ORDER_ITEM_ID"


class TransactionDetails(IncrementalDoordashStream):
    report_type = "TRANSACTION_DETAIL"
    cursor_field = "TIMESTAMP_LOCAL_DATE"
    primary_key = "TRANSACTION_ID"


class TemporaryDeactivations(IncrementalDoordashStream):
    report_type = "TEMPORARY_DEACTIVATION"
    cursor_field = "CREATED_AT_TIME"
    primary_key = ["STORE_ID", "CREATED_AT_TIME"]


class SourceDoordash(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            url_base = 'https://openapi.doordash.com/dataexchange/v1/reports'
            auth = TokenAuthenticator(token=config['api_key'])
            body = { 
                "store_ids": [],
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
                "report_type": "ORDER_DETAIL"
            }
            response = requests.post(url_base, headers=auth.get_auth_header(), json=body)
            response.raise_for_status()
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(token=config['api_key'])  
        return [OrderDetails(authenticator=auth, config=config), 
                TransactionDetails(authenticator=auth, config=config),
                TemporaryDeactivations(authenticator=auth, config=config)]
