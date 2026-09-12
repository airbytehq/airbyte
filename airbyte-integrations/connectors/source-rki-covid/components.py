#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor


class StatesAgeGroupsExtractor(RecordExtractor):
    """Extracts per-state age-group records from the states/age-groups endpoint.

    The API returns ``{"data": {<state_abbreviation>: {<age_group>: {...}}}}}``.
    This mirrors the legacy Python connector (``GermanyStatesAgeGroups``),
    which yields one record per state with the state abbreviation injected.
    """

    def extract_records(self, response: requests.Response, **kwargs) -> List[Mapping[str, Any]]:
        data = response.json().get("data", {})
        records = []
        for abbreviation, age_groups in data.items():
            record: Mapping[str, Any] = {"abbreviation": abbreviation}
            record.update(age_groups)
            records.append(record)
        return records


class StatesHistoryExtractor(RecordExtractor):
    """Extracts per-state history records from the states/history/* endpoints.

    The API returns ``{"data": {<state_abbreviation>: {"name": ..., "history": [...]}}}``.
    This mirrors the legacy Python connector (``ByStateRkiCovidStream``),
    which yields one record per history entry with the state name and
    abbreviation injected.
    """

    def extract_records(self, response: requests.Response, **kwargs) -> List[Mapping[str, Any]]:
        data = response.json().get("data", {})
        records = []
        for abbreviation, state in data.items():
            for record in state.get("history", []):
                record.update({"name": state.get("name"), "abbreviation": abbreviation})
                records.append(record)
        return records
