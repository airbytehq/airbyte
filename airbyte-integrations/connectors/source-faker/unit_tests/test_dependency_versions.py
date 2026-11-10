#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from importlib.metadata import version

from packaging.version import Version


def test_installed_airbyte_cdk_meets_declared_floor():
    assert Version(version("airbyte-cdk")) >= Version("6.62.0")
