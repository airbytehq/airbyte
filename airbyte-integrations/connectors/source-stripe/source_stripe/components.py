from typing import Iterable, Mapping, Any

import requests
from airbyte_cdk import RecordExtractor


class StripeDualStreamRecordExtractor(RecordExtractor):
    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        if response.json()["url"] == "/v1/events":
            for record in response.json()["data"]:
                item = record["data"]["object"]
                item["updated"] = record["created"]  # FIXME move to transformation
                item["pagination_id"] = record["id"]  # FIXME move to transformation
                if record["type"].endswith(".deleted"):
                    item["is_deleted"] = True
                yield item
        else:
            for record in response.json()["data"]:
                record["updated"] = record["created"]  # FIXME move to transformation
                record["pagination_id"] = record["id"]  # FIXME move to transformation
                yield record
