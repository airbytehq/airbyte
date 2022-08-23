#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from typing import MutableMapping, Any, Mapping

from .base import DateSlicesMixin, MixpanelStream


class Annotations(DateSlicesMixin, MixpanelStream):
    """List the annotations for a given date range.
    API Docs: https://developer.mixpanel.com/reference/annotations
    Endpoint: https://mixpanel.com/api/2.0/annotations

    New:

    API Docs: https://developer.mixpanel.com/reference/list-all-annotations-for-project
    Endpoint: https://mixpanel.com/api/app/projects/{projectId}/annotations


    Output example:
    {
        "annotations": [{
                "id": 640999
                "project_id": 2117889
                "date": "2021-06-16 00:00:00" <-- PLEASE READ A NOTE
                "description": "Looks good"
            }, {...}
        ]
    }

    NOTE: annotation date - is the date for which annotation was added, this is not the date when annotation was added
    That's why stream does not support incremental sync.
    """

    data_field: str = "annotations"
    primary_key: str = "id"

    @property
    def url_base(self):
        if self.projects:
            return "https://mixpanel.com/api/app/"
        else:
            return "https://mixpanel.com/api/2.0/"

    def path(self, stream_slice=None, **kwargs) -> str:
        if self.projects:
            return f"projects/{stream_slice['project_id']}/annotations"
        else:
            return "annotations"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        if self.projects:
            params.pop('project_id', None)
            params["fromDate"] = params.pop('from_date')
            params["toDate"] = params.pop('to_date')
        return params
