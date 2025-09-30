#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict, Optional

from unit_tests.conftest import get_source

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read


def read_helper(
    config: Dict[str, Any],
    catalog: ConfiguredAirbyteCatalog,
    state: Optional[Dict[str, Any]] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    source_state = state if state else {}
    source = get_source(config, source_state)
    return read(source, config, catalog, state, expecting_exception)
