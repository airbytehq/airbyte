# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from typing import Any, List, Mapping, Optional

import pytest
from source_google_ads.source import SourceGoogleAds

from airbyte_cdk.models import AirbyteStateMessage


@pytest.fixture(autouse=True)
def mock_oauth_call():
    yield


def create_source(
    config: Mapping[str, Any],
    catalog: Any = None,
    state: Optional[List[AirbyteStateMessage]] = None,
) -> SourceGoogleAds:
    return SourceGoogleAds(catalog=catalog, config=config, state=state)
