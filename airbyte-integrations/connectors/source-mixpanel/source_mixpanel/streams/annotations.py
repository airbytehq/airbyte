#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from .base import DateSlicesMixin, MixpanelStream


class Annotations(DateSlicesMixin, MixpanelStream):
    """List the annotations for a given date range.
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

    data_field: str = "results"
    primary_key: str = "id"

    @property
    def url_base(self):
        prefix = "eu." if self.region == "EU" else ""
        return f"https://{prefix}mixpanel.com/api/app/projects/"

    def path(self, **kwargs) -> str:
        return f"{self.project_id}/annotations"
