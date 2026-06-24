#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import importlib.metadata

import pytest
from packaging.version import Version


LANGCHAIN_CORE_VULN_THRESHOLD = Version("1.2.5")
CDK_MIN_SAFE_VERSION = Version("7.6.4")


@pytest.mark.parametrize(
    "package,min_version",
    [
        pytest.param("langchain-core", LANGCHAIN_CORE_VULN_THRESHOLD, id="GHSA-c67j-w6g6-q2cm"),
        pytest.param("airbyte-cdk", CDK_MIN_SAFE_VERSION, id="cdk-pins-safe-langchain"),
    ],
)
def test_dependency_above_vulnerability_threshold(package: str, min_version: Version) -> None:
    installed = Version(importlib.metadata.version(package))
    assert installed >= min_version, (
        f"{package}=={installed} is below the minimum safe version {min_version}"
    )
