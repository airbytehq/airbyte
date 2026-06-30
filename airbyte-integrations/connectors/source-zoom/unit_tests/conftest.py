#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import sys
from pathlib import Path


# Add the connector root to sys.path so that `components` can be imported directly,
# mirroring how the CDK resolves `source_declarative_manifest.components` at runtime.
_CONNECTOR_ROOT = Path(__file__).parent.parent
sys.path.append(str(_CONNECTOR_ROOT))
