#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime
from typing import Any, Iterable, List, Mapping, Optional, Tuple
from urllib.parse import urlparse

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream

from .adapters import adaptTypeToEnum, adaptSubTypeToEnum, adaptStatusToEnum

logger = logging.getLogger("airbyte")

base_url = "https://api.uptimerobot.com"


class SourceUptimeRobot(AbstractSource):
    jwt = None

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        api_key = config["api_key"]

        url = f"{base_url}/v2/getAccountDetails?api_key={api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.info(str(e))
                return False, "Invalid api_key"
            elif e.response.status_code == 404:
                logger.info(str(e))
                return False, f"Account not found"
            else:
                logger.info(str(e))
                return False, f"Error getting basic user info for UptimeRobot account. Unexpected error"

        logger.info(f"Connection check for UptimeRobot account successful.")
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        start_date = datetime.strptime(config['start_date'], '%Y-%m-%d')
        return [
            Monitors(api_key=config["api_key"], config=config, start_date=start_date),
            Status(api_key=config["api_key"], config=config, start_date=start_date),
        ]


class Monitors(HttpStream):
    url_base = base_url
    http_method = "POST"
    # Set this as a noop.
    primary_key = "id"

    def __init__(self, api_key: str, config: Mapping[str, Any], start_date: datetime, **kwargs):
        super().__init__()
        self.api_key = api_key
        self.start_date = start_date

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        if decoded_response["pagination"] is None or decoded_response["pagination"]["offset"] is None or decoded_response["pagination"]["total"] is None:
            return None
        else:
            offset = decoded_response["pagination"]["offset"]
            total = decoded_response["pagination"]["total"]
            limit = decoded_response["pagination"]["limit"]
            if limit - total > 0:
                return None
            return {
                "offset": offset+total,
            }

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = "0"
    ) -> str:
        return f"/v2/getMonitors"

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {
            "Cache-Control": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def request_body_data(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        offset = next_page_token["offset"] if next_page_token is not None else 0
        return {
            "format": "json",
            "offset": offset,
            "total": 5,
            "api_key": self.api_key,
        }

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        for monitor in response.json().get("monitors"):
            yield {
                "id": monitor["id"],
                "friendly_name": monitor["friendly_name"],
                "url": monitor["url"],
                "type": adaptTypeToEnum(monitor["type"]),
                "subtype": adaptSubTypeToEnum(monitor["subtype"] if "subtype" in monitor else None),
                "status": adaptStatusToEnum(monitor["status"]),
                "created_at": datetime.fromtimestamp(monitor["create_datetime"]),
                "interval": monitor["interval"],
            }


class Status(HttpStream):
    url_base = base_url
    http_method = "POST"
    # Set this as a noop.
    primary_key = None

    def __init__(self, api_key: str, config: Mapping[str, Any], start_date: datetime, **kwargs):
        super().__init__()
        self.api_key = api_key
        self.start_date = start_date

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        if decoded_response["pagination"] is None or decoded_response["pagination"]["offset"] is None or decoded_response["pagination"]["total"] is None:
            return None
        else:
            offset = decoded_response["pagination"]["offset"]
            total = decoded_response["pagination"]["total"]
            limit = decoded_response["pagination"]["limit"]
            if limit - total > 0:
                return None
            return {
                "offset": offset+total,
            }

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = "0"
    ) -> str:
        return f"/v2/getMonitors"

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {
            "Cache-Control": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def request_body_data(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        offset = next_page_token["offset"] if next_page_token is not None else 0
        return {
            "format": "json",
            "offset": offset,
            "total": 50,
            "logs": 1,
            "api_key": self.api_key,
        }

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        for monitor in response.json().get("monitors"):
            if "logs" in monitor:
                for log in monitor["logs"]:
                    yield {
                        "monitor_id": monitor["id"],
                        "friendly_name": monitor["friendly_name"],
                        "url": monitor["url"],
                        "type": adaptTypeToEnum(monitor["type"]),
                        "subtype": adaptSubTypeToEnum(monitor["subtype"] if "subtype" in monitor else None),
                        "status": adaptStatusToEnum(log["type"]),
                        "datetime": datetime.fromtimestamp(log["datetime"]),
                        "duration": log["duration"],
                    }
