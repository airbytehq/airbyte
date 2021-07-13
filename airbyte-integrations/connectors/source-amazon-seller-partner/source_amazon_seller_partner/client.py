#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import json
import pkgutil
import time
from datetime import datetime
from typing import Any, Dict, Generator, List, MutableMapping, Tuple

import pendulum
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, AirbyteStateMessage, AirbyteStream, Type

from .amazon import AmazonClient


class BaseClient:
    CONVERSION_WINDOW_DAYS = 14

    def __init__(
        self,
        refresh_token: str,
        lwa_app_id: str,
        lwa_client_secret: str,
        aws_secret_key: str,
        aws_access_key: str,
        role_arn: str,
        start_date: str,
        seller_id: str = "",
        marketplace: str = "USA",
    ):
        self.credentials = dict(
            refresh_token=refresh_token,
            lwa_app_id=lwa_app_id,
            lwa_client_secret=lwa_client_secret,
            aws_secret_key=aws_secret_key,
            aws_access_key=aws_access_key,
            role_arn=role_arn,
        )
        self.start_date = start_date
        self.seller_id = seller_id
        self._amazon_client = AmazonClient(credentials=self.credentials, marketplace=marketplace)

    def check_connection(self):
        updated_after = pendulum.now().subtract(days=self.CONVERSION_WINDOW_DAYS).to_date_string()
        return self._amazon_client.fetch_orders(updated_after, 10, None)

    def get_streams(self):
        streams = []
        for entity in self._amazon_client.get_entities():
            raw_schema = json.loads(pkgutil.get_data(self.__class__.__module__.split(".")[0], f"schemas/{entity}.json"))
            streams.append(AirbyteStream.parse_obj(raw_schema))
        return streams

    def read_stream(
        self, logger: AirbyteLogger, stream_name: str, state: MutableMapping[str, Any]
    ) -> Generator[AirbyteMessage, None, None]:
        cursor_field = self._amazon_client.get_cursor_for_stream(stream_name)
        cursor_value = self._get_cursor_or_none(state, stream_name, cursor_field) or self.start_date

        if pendulum.parse(cursor_value) > pendulum.now():
            yield self._state(state)
            return

        current_date = self._apply_conversion_window(cursor_value)

        logger.info(f"Started pulling data from {current_date}")
        HAS_NEXT = True
        NEXT_TOKEN = None
        PAGE = 1
        while HAS_NEXT:
            logger.info(f"Pulling for page: {PAGE}")
            response = self._amazon_client.fetch_orders(current_date, self._amazon_client.PAGECOUNT, NEXT_TOKEN)
            orders = response["Orders"]
            if "NextToken" in response:
                NEXT_TOKEN = response["NextToken"]
            HAS_NEXT = True if NEXT_TOKEN else False
            PAGE = PAGE + 1
            for order in orders:
                current_date = pendulum.parse(order[cursor_field]).to_date_string()
                cursor_value = max(current_date, cursor_value) if cursor_value else current_date
                yield self._record(stream=stream_name, data=order, seller_id=self.seller_id)

            if cursor_value:
                state[stream_name][cursor_field] = pendulum.parse(cursor_value).add(days=1).to_date_string()
                yield self._state(state)

            # Sleep for 2 seconds
            time.sleep(2)

    def read_reports(
        self, logger: AirbyteLogger, stream_name: str, state: MutableMapping[str, Any]
    ) -> Generator[AirbyteMessage, None, None]:
        cursor_field = self._amazon_client.get_cursor_for_stream(stream_name)
        cursor_value = self._get_cursor_or_none(state, stream_name, cursor_field) or self.start_date

        if pendulum.parse(cursor_value) > pendulum.now():
            yield self._state(state)
            return

        current_date = cursor_value

        while pendulum.parse(current_date) < pendulum.yesterday():
            logger.info(f"Started pulling data from {current_date}")
            start_date, end_date = self._get_date_parameters(current_date)

            # Request for the report
            logger.info(f"Requested report from {start_date} to {end_date}")
            response = self._amazon_client.request_report(stream_name, start_date, end_date)
            reportId = response["reportId"]

            # Wait for the report status
            status, document_id = BaseClient._wait_for_report(logger, self._amazon_client, reportId)

            # Move to next month when the report is CANCELLED
            if status is False:
                current_date = self._increase_date_by_month(current_date)
                continue

            # Pull data for a report
            data = self._amazon_client.get_report_document(document_id)

            # Loop through all records and yield
            for row in self._get_records(data):
                current_cursor_value = pendulum.parse(row[cursor_field]).to_date_string()
                cursor_value = max(current_cursor_value, cursor_value) if cursor_value else current_cursor_value
                yield self._record(stream=stream_name, data=row, seller_id=self.seller_id)

            if cursor_value:
                state[stream_name][cursor_field] = pendulum.parse(cursor_value).add(days=1).to_date_string()
                yield self._state(state)

            current_date = self._increase_date_by_month(current_date)

    def _get_records(self, data: Dict[str, Any]):
        records = data["document"].splitlines()
        headers = records[0].split("\t")
        records = records[1:]
        return self._convert_array_into_dict(headers, records)

    def _apply_conversion_window(self, current_date: str) -> str:
        return pendulum.parse(current_date).subtract(days=self.CONVERSION_WINDOW_DAYS).to_date_string()

    @staticmethod
    def _wait_for_report(logger, amazon_client: AmazonClient, reportId: str):
        MAX_SLEEP_TIME = 512
        current_sleep_time = 4

        logger.info(f"Waiting for the report {reportId}")
        while True:
            response = amazon_client.get_report(reportId)
            if response["processingStatus"] == "DONE":
                logger.info("Report status: DONE")
                document_id = response["reportDocumentId"]
                return True, document_id
            elif response["processingStatus"] == "CANCELLED" or response["processingStatus"] == "FATAL":
                # The report was cancelled. There are two ways a report can be cancelled:
                # an explicit cancellation request before the report starts processing,
                # or an automatic cancellation if there is no data to return.
                logger.info(f"Report CANCELLED: {reportId}")
                return False, None

            if current_sleep_time > MAX_SLEEP_TIME:
                logger.error("Max wait reached")
                raise Exception("Max wait time reached")

            logger.info(f"Sleeping for {current_sleep_time}")
            time.sleep(current_sleep_time)
            current_sleep_time = current_sleep_time * 2

    @staticmethod
    def _convert_array_into_dict(headers: List[Dict[str, Any]], values: List[Dict[str, Any]]):
        records = []
        for value in values:
            records.append(dict(zip(headers, value.split("\t"))))
        return records

    @staticmethod
    def _increase_date_by_month(current_date: str) -> str:
        return pendulum.parse(current_date).add(months=1).to_date_string()

    @staticmethod
    def _get_date_parameters(current_date: str) -> Tuple[str, str]:
        start_date = pendulum.parse(current_date)
        end_date = pendulum.parse(current_date).add(months=1)
        if end_date > pendulum.yesterday():
            end_date = pendulum.yesterday()

        return start_date.to_date_string(), end_date.to_date_string()

    @staticmethod
    def _get_cursor_or_none(state: MutableMapping[str, Any], stream_name: str, cursor_name: str) -> Any:
        if state and stream_name in state and cursor_name in state[stream_name]:
            return state[stream_name][cursor_name]
        else:
            return None

    @staticmethod
    def _record(stream: str, data: Dict[str, Any], seller_id: str) -> AirbyteMessage:
        now = int(datetime.now().timestamp()) * 1000
        if seller_id:
            data["seller_id"] = seller_id
        return AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data=data, emitted_at=now))

    @staticmethod
    def _state(data: MutableMapping[str, Any]) -> AirbyteMessage:
        return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))
