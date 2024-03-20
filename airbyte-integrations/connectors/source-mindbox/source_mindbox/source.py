#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import csv
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from io import BytesIO, TextIOWrapper
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.availability_strategy import (
    HttpAvailabilityStrategy as _HttpAvailabilityStrategy,
)

from .mindbox_service import MindboxService

logger = logging.getLogger("airbyte")
CONFIG_DATE_FORMAT = "%Y-%m-%d"


class HttpAvailabilityStrategy(_HttpAvailabilityStrategy):
    def check_availability(self, *args, **kwargs):
        return True, None


# Basic full refresh stream
class MindboxStream(HttpStream, ABC):
    url_base = None
    wait_for_export_complete_interval = 60

    availability_strategy = HttpAvailabilityStrategy

    @property
    @abstractmethod
    def operation_name(self) -> str:
        """Name of operation to task on current stream class

        Returns:
            str: operation_name
        """

    @property
    @abstractmethod
    def use_date_range(self) -> bool:
        """Should stream use date_from and date_to fields as date range payload

        Returns:
            bool: should stream use date range?
        """

    def path(self, *args, **kwargs) -> str:
        return None

    def __init__(self, mindbox_service: MindboxService, date_from: datetime, date_to: datetime):
        super().__init__(authenticator=None)
        self._mindbox_service = mindbox_service
        self._export_id = None
        self._date_from = date_from
        self._date_to = date_to

    def start_export_preload(self):
        start_task_kwargs = dict(operation=self.operation_name)
        if self.use_date_range:
            start_task_kwargs["json_payload"] = {
                "sinceDateTimeUtc": datetime.strftime(self._date_from, "%Y-%m-%d %H:%M"),
                "tillDateTimeUtc": datetime.strftime(self._date_to, "%Y-%m-%d %H:%M"),
            }
        status = self._mindbox_service.start_operation_task(**start_task_kwargs)
        self._export_id = status["exportId"]
        return status

    def wait_for_export_complete(self):
        if not self._export_id:
            raise Exception(
                f"Can't wait for export completed. Operation "
                f"{self.operation_name} for stream {self.name} not started",
            )
        return self._mindbox_service.wait_operation_task_succeeded(
            operation=self.operation_name,
            export_id=self._export_id,
            wait_seconds=self.wait_for_export_complete_interval,
        )

    def read_records(self, *args, **kwargs) -> Iterable[StreamData]:
        self.start_export_preload()
        completed_export = self.wait_for_export_complete()
        for url in completed_export["exportResult"]["urls"]:
            req = requests.Request("GET", url)
            prepared_request = req.prepare()
            response = self._send(prepared_request, {})
            yield from self.parse_response(response)
        # Always return an empty generator just in case no records were ever yielded
        yield from []

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        csv_content = response.content.decode("utf-8-sig")
        csv_file = TextIOWrapper(
            BytesIO(csv_content.encode("utf-8-sig")),
            encoding="utf-8-sig",
        )
        reader = csv.DictReader(csv_file, delimiter=";")
        yield from reader


class MailingEntities(MindboxStream):
    use_date_range = False
    primary_key = "MailingName"
    operation_name = "EksportEntityRassylok"


class EmailClicks(MindboxStream):
    use_date_range = True
    primary_key = "CustomerActionRootActionIdsMindboxId"
    operation_name = "EksportKlikovEmail"


class Customers(MindboxStream):
    use_date_range = False
    primary_key = "CustomerIdsMindboxId"
    operation_name = "EksportPodpisannyxKlientov"


class CustomerSegments(MindboxStream):
    use_date_range = False
    primary_key = "CustomerSegmentCustomerIdsMindboxId"
    operation_name = "EksportPodpischikovVDinamike"


class CustomerSegmentsEmail(MindboxStream):
    use_date_range = False
    primary_key = "CustomerSegmentCustomerIdsMindboxId"
    operation_name = "EksportPodpischikovVDinamikeEmail"


class CustomerSegmentsApppush(MindboxStream):
    use_date_range = False
    primary_key = "CustomerSegmentCustomerIdsMindboxId"
    operation_name = "EksportPodpischikovVDinamikeApppush"


class CustomerSegmentsApppushAndroid(MindboxStream):
    use_date_range = False
    primary_key = "CustomerSegmentCustomerIdsMindboxId"
    operation_name = "EksportPodpischikovVDinamikeApppushAndroid"


class CustomerSegmentsApppushIos(MindboxStream):
    use_date_range = False
    primary_key = "CustomerSegmentCustomerIdsMindboxId"
    operation_name = "EksportPodpischikovVDinamikeApppushIos"


class CustomerSegmentsWebpush(MindboxStream):
    use_date_range = False
    primary_key = "CustomerSegmentCustomerIdsMindboxId"
    operation_name = "EksportPodpischikovVDinamikeWebpush"


class Attribution(MindboxStream):
    use_date_range = False
    primary_key = "OrderIdsTravelataOrderId"
    operation_name = "EksportAtribucii"


class EmailUnsubscribes(MindboxStream):
    use_date_range = False
    primary_key = "CustomerSegmentCustomerIdsMindboxId"
    operation_name = "EksportEmailOtpisannyx"


class ExportSub(MindboxStream):
    use_date_range = False
    primary_key = "CustomerIdsMindboxId"
    operation_name = "ExportSub"


# Source
class SourceMindbox(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    @staticmethod
    def prepare_config_datetime(config: Mapping[str, Any]) -> Mapping[str, Any]:
        date_range = config["date_range"]
        range_type = config["date_range"]["date_range_type"]
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        prepared_range = {}
        if range_type == "custom_date":
            prepared_range["date_from"] = date_range["date_from"]
            prepared_range["date_to"] = date_range["date_to"]
        elif range_type == "from_date_from_to_today":
            prepared_range["date_from"] = date_range["date_from"]
            if date_range["should_load_today"]:
                prepared_range["date_to"] = today
            else:
                prepared_range["date_to"] = today - timedelta(days=1)
        elif range_type == "last_n_days":
            prepared_range["date_from"] = today - timedelta(days=date_range["last_days_count"])
            if date_range["should_load_today"]:
                prepared_range["date_to"] = today
            else:
                prepared_range["date_to"] = today - timedelta(days=1)
        else:
            raise ValueError("Invalid date_range_type")

        if isinstance(prepared_range["date_from"], str):
            prepared_range["date_from"] = datetime.strptime(
                prepared_range["date_from"], CONFIG_DATE_FORMAT
            )

        if isinstance(prepared_range["date_to"], str):
            prepared_range["date_to"] = datetime.strptime(
                prepared_range["date_to"], CONFIG_DATE_FORMAT
            )
        config["prepared_date_range"] = prepared_range
        return config

    def transform_config(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return self.prepare_config_datetime(config)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self.transform_config(config)
        mindbox_service = MindboxService(
            endpoint_id=config["endpoint_id"],
            secret_key=config["secret_key"],
            logger=logger,
        )
        shared_kwargs = dict(
            mindbox_service=mindbox_service,
            date_from=config["prepared_date_range"]["date_from"],
            date_to=config["prepared_date_range"]["date_to"],
        )
        return [
            MailingEntities(**shared_kwargs),
            EmailClicks(**shared_kwargs),
            Customers(**shared_kwargs),
            CustomerSegments(**shared_kwargs),
            CustomerSegmentsEmail(**shared_kwargs),
            CustomerSegmentsApppush(**shared_kwargs),
            CustomerSegmentsWebpush(**shared_kwargs),
            Attribution(**shared_kwargs),
            EmailUnsubscribes(**shared_kwargs),
            CustomerSegmentsApppushAndroid(**shared_kwargs),
            CustomerSegmentsApppushIos(**shared_kwargs),
            ExportSub(**shared_kwargs),
        ]
