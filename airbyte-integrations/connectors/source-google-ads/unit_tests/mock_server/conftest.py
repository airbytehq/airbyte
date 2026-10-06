# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from typing import Any, List, Mapping, Optional

from source_google_ads.source import SourceGoogleAds

from airbyte_cdk.models import AirbyteStateMessage


def create_source(
    config: Mapping[str, Any],
    catalog: Any = None,
    state: Optional[List[AirbyteStateMessage]] = None,
) -> SourceGoogleAds:
    return SourceGoogleAds(catalog=catalog, config=config, state=state)
