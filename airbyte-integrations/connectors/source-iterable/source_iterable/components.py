#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
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

    The Iterable export API returns `itblInternal.*` and `itblDS.*` as flat dotted
    keys rather than nested objects, so those are preserved as-is at the top level.
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
            # Fields used for sending messages
            "country",
            "devices",
            "ip",
            "locale",
            "phoneNumber",
            "profile",
            "timeZone",
        }
    )

    # itblInternal.* and itblDS.* come as flat dotted keys from the export API.
    ITBL_PREFIXES = ("itblInternal.", "itblDS.")

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        jsonl_records = super().extract_records(response=response)
        for record_dict in jsonl_records:
            standard: dict[str, Any] = {}
            data: dict[str, Any] = {}
            for key, value in record_dict.items():
                if key in self.STANDARD_FIELDS or key.startswith(self.ITBL_PREFIXES):
                    standard[key] = value
                else:
                    data[key] = value
            standard["data"] = data
            yield standard
