#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict, Optional

from source_bing_ads.source import SourceBingAds

from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, discover, read


def source(
    config: Dict[str, Any] = None, catalog: ConfiguredAirbyteCatalog = None, state: Optional[Dict[str, Any]] = None
) -> SourceBingAds:
    if not catalog:
        catalog = CatalogBuilder().with_stream("fake_stream", SyncMode.full_refresh).build()
    return SourceBingAds(catalog=catalog, config=config, state=state)
