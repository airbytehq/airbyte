#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from calendar import timegm
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import feedparser
import pytz
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from dateutil.parser import parse

item_keys = [
    "title",
    "link",
    "description",
    "author",
    "category",
    "comments",
    "enclosure",
    "guid",
]


def convert_item_to_mapping(item) -> Mapping:
    mapping = {}

    for item_key in item_keys:
        try:
            mapping[item_key] = item[item_key]
        except (AttributeError, KeyError):
            pass

    try:
        # get datetime in UTC
        dt = datetime.utcfromtimestamp(timegm(item.published_parsed))
        # make sure that the output string is labeled as UTC
        dt_tz = dt.replace(tzinfo=pytz.UTC)
        mapping["published"] = dt_tz.isoformat()
    except (AttributeError, KeyError):
        pass

    return mapping


def is_newer(item, initial_state_date) -> bool:
    try:
        current_record_date = parse(item["published"])
    except Exception:
        current_record_date = None

    if initial_state_date is None:
        # if we don't have initial state they are all new
        return True
    elif current_record_date is None:
        # if we can't parse the item timestamp, we should return it
        return True
    else:
        return current_record_date > initial_state_date


# Basic stream
class RssStream(HttpStream, ABC):
    # empty URL base since the stream can have its own full URL
    url_base = ""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # no pagination enabled
        return None

    # since we only have one response for the stream, we should only return records newer than the initial state object if incremental
    def parse_response(self, response: requests.Response, stream_state: MutableMapping[str, Any], **kwargs) -> Iterable[Mapping]:
        feed = feedparser.parse(response.text)

        try:
            initial_state_date = parse(stream_state["published"])
        except Exception:
            initial_state_date = None

        # go through in reverse order which helps the state comparisons
        all_item_mappings = [convert_item_to_mapping(item) for item in feed.entries[::-1]]

        # will only filter if we have a state object, so it's incremental
        yield from [item for item in all_item_mappings if is_newer(item, initial_state_date)]


# Basic incremental stream
class IncrementalRssStream(RssStream, ABC):
    # no reason to checkpoint if it's reading individual files without pagination
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        return "published"

    # this will fail if the dates aren't parseable, but that means incremental isn't possible anyway for that feed
    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        try:
            latest_record_date = parse(latest_record["published"])
            latest_record_state = {"published": latest_record["published"]}
        except Exception:
            latest_record_date = None

        try:
            current_record_date = parse(current_stream_state["published"])
        except Exception:
            current_record_date = None

        if latest_record_date and current_record_date:
            if latest_record_date > current_record_date:
                return latest_record_state
            else:
                return current_stream_state
        if latest_record_date:
            return latest_record_state
        if current_record_date:
            return current_stream_state
        else:
            return {}


class Items(IncrementalRssStream):
    def __init__(self, url: str):
        super().__init__()
        self.url = url

    primary_key = None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.url


# Source
class SourceRss(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            resp = requests.get(config.get("url"))
            status = resp.status_code
            if status == 200:
                return True, None
            else:
                return False, f"Unable to connect to RSS Feed (received status code: {status})"
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [Items(config.get("url"))]
