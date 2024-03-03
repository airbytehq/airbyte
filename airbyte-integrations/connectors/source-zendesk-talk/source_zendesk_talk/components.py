from dataclasses import dataclass
import requests
from typing import List

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.types import Record


@dataclass
class IVRMenusRecordExtractor(RecordExtractor):
    def extract_records(self, response: requests.Response) -> List[Record]:
        ivrs = response.json().get("ivrs", [])
        records = []
        for ivr in ivrs:
            for menu in ivr.get("menus", []):
                records.append({"ivr_id": ivr["id"], **menu})
        return records


@dataclass
class IVRRoutesRecordExtractor(RecordExtractor):
    def extract_records(self, response: requests.Response) -> List[Record]:
        ivrs = response.json().get("ivrs", [])
        records = []
        for ivr in ivrs:
            for menu in ivr.get("menus", []):
                for route in menu.get("routes", []):
                    records.append({"ivr_id": ivr["id"], "ivr_menu_id": menu["id"], **route})
        return records
