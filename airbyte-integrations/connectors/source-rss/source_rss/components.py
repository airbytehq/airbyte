#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import logging
from calendar import timegm
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, List, Mapping, Optional

import feedparser
import pytz
import requests
from dateutil.parser import parse

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.types import StreamSlice
from airbyte_cdk.sources.streams.core import Stream


class CustomExtractor(RecordExtractor):
    def extract_records(self, response: requests.Response, **kwargs) -> List[Mapping[str, Any]]:
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
                dt = datetime.utcfromtimestamp(timegm(item.published_parsed))
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
                return True
            elif current_record_date is None:
                return True
            else:
                return current_record_date > initial_state_date

        feed = feedparser.parse(response.text)
        try:
            initial_state_date = parse(feed["published"])
        except Exception:
            initial_state_date = None

        all_item_mappings = [convert_item_to_mapping(item) for item in feed.entries[::-1]]
        new_items = [item for item in all_item_mappings if is_newer(item, initial_state_date)]
        return new_items
