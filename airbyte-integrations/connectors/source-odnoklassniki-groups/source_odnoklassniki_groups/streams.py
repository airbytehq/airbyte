from __future__ import annotations

import hashlib
import logging
from datetime import date, datetime, time, timedelta
from json import JSONDecodeError
from time import sleep
from typing import Type, Mapping, Any, List, Iterable, Optional
from urllib.parse import urlencode

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream

from source_odnoklassniki_groups.auth import OKCredentials
from source_odnoklassniki_groups.schemas import GetStatTrends
from source_odnoklassniki_groups.types import IsSuccess, Message

log = logging.getLogger(__name__)


def check_group_stream_connection(credentials: OKCredentials, gid: str) -> tuple[IsSuccess, Optional[Message]]:
    timestamp_now = str(int(datetime.timestamp(datetime.now()))).ljust(13, "0")
    timestamp_1h = str(int(datetime.timestamp(datetime.now() - timedelta(hours=1)))).ljust(13, "0")
    application_key = credentials.application_key.get_secret_value()
    params = {
        "application_key": application_key,
        "fields": "COMMENTS",
        "format": "json",
        "gid": gid,
        "method": "group.getStatTrends",
        "sig": hashlib.md5(
            f"application_key={application_key}"
            f"end_time={timestamp_now}"
            f"fields=COMMENTS"
            f"format=json"
            f"gid={gid}"
            f"method=group.getStatTrends"
            f"start_time={timestamp_1h}"
            f"{credentials.session_secret_key.get_secret_value()}".encode()
        ).hexdigest(),
        "access_token": credentials.access_token.get_secret_value(),
        "start_time": timestamp_1h,
        "end_time": timestamp_now,
    }
    try:
        response = requests.get(f"https://api.ok.ru/fb.do?{urlencode(params)}")
        if 200 <= response.status_code < 300:
            return True, None
        return False, f"Response status code: {response.status_code}. Body: {response.text}"
    except Exception as e:
        return False, str(e)


class GetStatTrendsStream(Stream):
    SCHEMA: Type[GetStatTrends] = GetStatTrends
    URL: str = "https://api.ok.ru/fb.do"
    METHOD: str = "group.getStatTrends"

    def __init__(self, credentials: OKCredentials, gids: List[str], date_from: date | None, date_to: date | None):
        self.credentials = credentials
        self.gids = gids
        self.date_from = date_from
        self.date_to = date_to

        self._start_timestamp = int(datetime.timestamp(datetime.combine(self.date_from, time()))) if self.date_from else None
        self._end_timestamp = int(datetime.timestamp(datetime.combine(self.date_to, time(23, 59, 59)))) if self.date_to else None
        self._fields = [
            "COMMENTS",
            "COMPLAINTS",
            "CONTENT_OPENS",
            "ENGAGEMENT",
            "FEEDBACK",
            "HIDES_FROM_FEED",
            "LEFT_MEMBERS",
            "LIKES",
            "LINK_CLICKS",
            "MEMBERS_COUNT",
            "MEMBERS_DIFF",
            "MUSIC_PLAYS",
            "NEGATIVES",
            "NEW_MEMBERS",
            "NEW_MEMBERS_TARGET",
            "PAGE_VISITS",
            "PHOTO_OPENS",
            "REACH",
            "REACH_EARNED",
            "REACH_MOB",
            "REACH_MOBWEB",
            "REACH_OWN",
            "REACH_WEB",
            "RENDERINGS",
            "RESHARES",
            "TOPIC_OPENS",
            "VIDEO_PLAYS",
            "VOTES",
        ]
        self._fields_str = ",".join(self._fields)

    @property
    def primary_key(self) -> None:
        return None

    def get_json_schema(self) -> Mapping[str, Any]:
        return self.SCHEMA.schema()

    @property
    def start_time(self) -> str | None:
        if not self._start_timestamp:
            return
        return str(self._start_timestamp).ljust(13, "0")

    @property
    def end_time(self) -> str | None:
        if not self._end_timestamp:
            return
        return str(self._end_timestamp).ljust(13, "0")

    def get_url(self, gid: str) -> str:
        params = {
            "application_key": self.credentials.application_key.get_secret_value(),
            "fields": self._fields_str,
            "format": "json",
            "gid": gid,
            "method": self.METHOD,
            "sig": self._calculate_sig(gid),
            "access_token": self.credentials.access_token.get_secret_value(),
        }
        if self._start_timestamp:
            params["start_time"] = self.start_time
        if self._end_timestamp:
            params["end_time"] = self.end_time
        return f"{self.URL}?{urlencode(params)}"

    def _calculate_sig(self, gid: str) -> str:
        secret_key = self.credentials.session_secret_key.get_secret_value()
        request_data = {
            "application_key": self.credentials.application_key.get_secret_value(),
            "fields": self._fields_str,
            "format": "json",
            "gid": gid,
            "method": self.METHOD,
        }
        if self._start_timestamp:
            request_data["start_time"] = self.start_time
        if self._end_timestamp:
            request_data["end_time"] = self.end_time
        sorted_request_data = dict(sorted(request_data.items()))
        request_str = "".join([f"{key}={value}" for key, value in sorted_request_data.items()]) + secret_key
        sig = hashlib.md5(request_str.encode()).hexdigest()
        return sig

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        for gid in self.gids:
            is_success = False
            attempts_count = 0
            while attempts_count < 3:
                try:
                    response = requests.get(self.get_url(gid))
                except Exception as e:
                    log.error(f"Request to OKAPI failed: {str(e)}")
                    attempts_count += 1
                    sleep(20)
                    continue

                if response.status_code == 200:
                    try:
                        if record := response.json():
                            yield self.SCHEMA(gid=gid, **record).dict()
                    except JSONDecodeError:
                        pass
                    is_success = True
                    break

                else:
                    raise Exception(f"Gid: '{gid}'. Status code: {response.status_code}. Body: {response.text}")

            if not is_success:
                raise Exception(f"Failed to load data from OKAPI in 3 attempts for gid '{gid}'")
