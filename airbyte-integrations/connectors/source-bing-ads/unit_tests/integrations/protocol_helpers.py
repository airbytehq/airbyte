#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict, Optional

from source_bing_ads.source import SourceBingAds

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read


def _source(catalog: ConfiguredAirbyteCatalog, config: Dict[str, Any], state: Optional[Dict[str, Any]]) -> SourceBingAds:
    return SourceBingAds(catalog=catalog, config=config, state=state)


def read_helper(
    config: Dict[str, Any],
    catalog: ConfiguredAirbyteCatalog,
    state: Optional[Dict[str, Any]] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    source_state = state if state else {}
    source = _source(catalog=catalog, config=config, state=source_state)
    return read(source, config, catalog, state, expecting_exception)
