#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from .base import DateSlicesMixin, MixpanelStream


class Annotations(DateSlicesMixin, MixpanelStream):
    """List the annotations for a given date range.
    API Docs: https://developer.mixpanel.com/reference/annotations
    Endpoint: https://mixpanel.com/api/2.0/annotations

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

    def path(self, **kwargs) -> str:
        return "annotations"
