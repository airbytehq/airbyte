#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Optional

# SET THESE BEFORE USING THE SCRIPT
MODULE_NAME: str = "strictness_level_migration"
GITHUB_PROJECT_NAME: Optional[str] = "SAT-high-test-strictness-level"
COMMON_ISSUE_LABELS: List[str] = ["area/connectors", "team/connectors-python", "type/enhancement", "test-strictness-level"]
ISSUE_TITLE: str = "enable `high` test strictness level in connector acceptance test"
