#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import importlib.metadata

from packaging.version import Version


CDK_MIN_SAFE_VERSION = Version("7.6.4")


def test_cdk_version_above_langchain_vuln_threshold() -> None:
    """CDK >= 7.6.4 pins langchain-core >= 1.2.5, fixing GHSA-c67j-w6g6-q2cm."""
    installed = Version(importlib.metadata.version("airbyte-cdk"))
    assert installed >= CDK_MIN_SAFE_VERSION, (
        f"airbyte-cdk=={installed} is below the minimum safe version {CDK_MIN_SAFE_VERSION}"
    )
