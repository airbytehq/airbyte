# Copyright (c) 2026 Canonical, all rights reserved.

"""Custom components for LiveChat source connector."""

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor


@dataclass
class FlattenChatGreetingsConversion(RecordExtractor):
    """Record extractor for the chat_greetings_conversion_report stream."""

    def extract_records(
        self,
        response: requests.Response,
        **kwargs,
    ) -> Iterable[Mapping[str, Any]]:
        """
        Transforms the response from nested dates and IDs to a flat list of records.
        Before (API Response):
            "records": {
                "2026-01-01": {
                    "1234": {
                        "accepted": 0,
                        ...
                    }
                }
            }
        After (Yielded Output):
            {
                "greeting_id": "1559",
                "report_date": "2026-01-04",
                "accepted": 0,
                ...
            }
        """
        records = response.json().get("records", {})
        for report_date, report_data in records.items():
            for record_id, record_data in report_data.items():
                record = {
                    "greeting_id": record_id,
                    "report_date": report_date,
                }
                record.update(record_data)
                yield record


@dataclass
class FlattenQueuedVisitorsLeft(RecordExtractor):
    """Record extractor for the queued_visitors_left_report stream."""

    def extract_records(self, response: requests.Response, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Transforms the response from a map of chat IDs to a flat list of records.
        Before (API Response):
            "records": {
                "SS0C6WIHKF": {
                    "visitor": {...},
                    "queue": {...},
                    ...
                }
            }
        After (Yielded Output):
            {
                "chat_id": "SS0C6WIHKF",
                "visitor": {...},
                "queue": {...},
                ...
            }
        """
        records = response.json().get("records", {})
        for chat_id, record_data in records.items():
            record = {"chat_id": chat_id}
            record.update(record_data)
            yield record
