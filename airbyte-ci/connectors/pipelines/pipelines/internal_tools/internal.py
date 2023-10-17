#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from enum import Enum


class INTERNAL_TOOL_PATHS(str, Enum):
    CI_CREDENTIALS = "airbyte-ci/connectors/ci_credentials"
    CONNECTOR_OPS = "airbyte-ci/connectors/connector_ops"
    METADATA_SERVICE = "airbyte-ci/connectors/metadata_service/lib"
