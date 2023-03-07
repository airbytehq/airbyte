#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, List, Mapping, Optional

import requests
from airbyte_cdk.models import SyncMode

from .cohorts import Cohorts
from .engage import Engage


class CohortMembers(Engage):
    """Return list of users grouped by cohort"""

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        # example: {"filter_by_cohort": {"id": 1343181}}
        return {"filter_by_cohort": stream_slice}

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        if sync_mode == SyncMode.incremental:
            self.set_cursor(cursor_field)

        stream_slices = []
        # full refresh is needed because even though some cohorts might already have been read
        # they can still have new members added
        cohorts = Cohorts(**self.get_stream_params()).read_records(SyncMode.full_refresh)
        for cohort in cohorts:
            stream_slices.append({"id": cohort["id"]})

        return stream_slices

    def process_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        records = super().process_response(response, **kwargs)
        for record in records:
            record["cohort_id"] = stream_slice["id"]
            yield record
