#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Mapping

import requests

from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor


@dataclass
class EventsRecordExtractor(DpathExtractor):
    common_fields = ("itblInternal", "_type", "createdAt", "email")

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        jsonl_records = super().extract_records(response=response)
        for record_dict in jsonl_records:
            record_dict_common_fields = {}
            for field in self.common_fields:
                record_dict_common_fields[field] = record_dict.pop(field, None)
            yield {**record_dict_common_fields, "data": record_dict}


@dataclass
class UsersRecordExtractor(DpathExtractor):
    """Extracts user records, keeping standard Iterable-managed fields at the top level
    and placing all custom/tenant-specific dataFields into a generic `data` object.

    Standard fields are those documented at:
    https://support.iterable.com/hc/en-us/articles/217744303-User-Profile-Fields-Used-by-Iterable

    The Iterable export API flattens nested objects into dotted keys (e.g.
    `itblInternal.emailDomain`), so Iterable-internal fields are listed in their flat
    dotted form. Keys not listed here - including Iterable-internal dotted keys that
    are not declared in the stream schema - are routed into `data` so destinations
    that materialize only declared fields never drop them.
    """

    # Fields documented by Iterable as managed or used for sending messages.
    # Reference: https://support.iterable.com/hc/en-us/articles/217744303
    STANDARD_FIELDS = frozenset(
        {
            # Unique identifiers
            "email",
            "userId",
            # Managed by Iterable
            "emailListIds",
            "itblUserId",
            "knownLitigatorFilter",
            "profileUpdatedAt",
            "receivedSMSDisclaimer",
            "signupDate",
            "signupSource",
            "subscribedMessageTypeIds",
            "unsubscribedChannelIds",
            "unsubscribedMessageTypeIds",
            "userListIds",
            # Geolocation fields populated by Iterable from the user's IP
            "city",
            "region",
            # Fields used for sending messages
            "country",
            "devices",
            "ip",
            "locale",
            "phoneNumber",
            "profile",
            "timeZone",
            "whatsAppPhoneNumber",
            # Iterable-internal fields (the export returns them as flat dotted keys)
            "itblInternal.emailDomain",
            "itblInternal.phoneCountry",
            "itblInternal.phoneType",
            "itblInternal.documentCreatedAt",
            "itblInternal.documentUpdatedAt",
            "itblInternal.isUnknownUser",
            "itblDS.brandAffinityLabel",
            "itblDS.predictiveGoals",
        }
    )

    # The export API emits these as space-separated timestamps ("2021-04-14 16:52:31 +00:00")
    # while the schema declares format: date-time (RFC3339); normalize so typed destinations
    # do not null the values into _airbyte_meta.changes.
    TIMESTAMP_FIELDS = (
        "signupDate",
        "profileUpdatedAt",
        "itblInternal.documentCreatedAt",
        "itblInternal.documentUpdatedAt",
    )
    _TIMESTAMP_FORMATS = (
        "%Y-%m-%d %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S.%f %z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
    )

    @classmethod
    def _normalize_timestamp(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        for fmt in cls._TIMESTAMP_FORMATS:
            try:
                return datetime.strptime(value, fmt).isoformat()
            except ValueError:
                continue
        return value

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        jsonl_records = super().extract_records(response=response)
        for record_dict in jsonl_records:
            standard: dict[str, Any] = {}
            data: dict[str, Any] = {}
            for key, value in record_dict.items():
                if key in self.STANDARD_FIELDS:
                    standard[key] = value
                else:
                    data[key] = value
            for field in self.TIMESTAMP_FIELDS:
                if field in standard:
                    standard[field] = self._normalize_timestamp(standard[field])
            standard["data"] = data
            yield standard
