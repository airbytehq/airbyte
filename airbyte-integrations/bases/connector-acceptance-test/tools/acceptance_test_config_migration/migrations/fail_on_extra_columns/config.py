#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Optional

# SET THESE BEFORE USING THE SCRIPT
MODULE_NAME: str = "fail_on_extra_columns"
GITHUB_PROJECT_NAME: Optional[str] = None
COMMON_ISSUE_LABELS: List[str] = ["area/connectors", "team/connectors-python", "type/enhancement", "column-selection-sources"]
ISSUE_TITLE: str = "Add undeclared columns to spec"
