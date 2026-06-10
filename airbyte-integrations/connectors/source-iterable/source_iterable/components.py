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

    The Iterable export API returns `itblInternal.*` as flat dotted keys rather than
    a nested object, so those are preserved as-is at the top level.
    """

    STANDARD_FIELDS = frozenset(
        {
            "email",
            "userId",
            "itblUserId",
            "firstName",
            "lastName",
            "signupDate",
            "signupSource",
            "profileUpdatedAt",
            "emailListIds",
            "subscribedMessageTypeIds",
            "unsubscribedMessageTypeIds",
            "unsubscribedChannelIds",
            "phoneNumber",
            "phoneNumberCarrier",
            "phoneNumberCountryPrefix",
            "phoneNumberIsVoip",
            "phoneNumberLineType",
            "phoneNumberUpdatedAt",
        }
    )

    ITBL_INTERNAL_PREFIX = "itblInternal."

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        jsonl_records = super().extract_records(response=response)
        for record_dict in jsonl_records:
            standard: dict[str, Any] = {}
            data: dict[str, Any] = {}
            for key, value in record_dict.items():
                if key in self.STANDARD_FIELDS or key.startswith(self.ITBL_INTERNAL_PREFIX):
                    standard[key] = value
                else:
                    data[key] = value
            standard["data"] = data
            yield standard
