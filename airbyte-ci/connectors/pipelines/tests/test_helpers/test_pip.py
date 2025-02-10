# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import pytest

from pipelines.helpers.pip import is_package_published


@pytest.mark.parametrize(
    "package_name, version, registry_url, expected",
    [
        pytest.param(None, None, "https://pypi.org/pypi", False, id="package_name and version are None"),
        pytest.param(None, "0.2.0", "https://pypi.org/pypi", False, id="package_name is None"),
        pytest.param("airbyte-source-pokeapi", None, "https://pypi.org/pypi", False, id="version is None"),
        pytest.param("airbyte-source-pokeapi", "0.2.0", "https://pypi.org/pypi", True, id="published on pypi"),
        pytest.param("airbyte-source-pokeapi", "0.1.0", "https://pypi.org/pypi", False, id="version not published on pypi"),
        pytest.param("airbyte-source-nonexisting", "0.1.0", "https://pypi.org/pypi", False, id="package not published on pypi"),
        pytest.param("airbyte-source-pokeapi", "0.2.1", "https://test.pypi.org/pypi", True, id="published on test.pypi"),
        pytest.param("airbyte-source-pokeapi", "0.1.0", "https://test.pypi.org/pypi", False, id="version not published on test.pypi"),
        pytest.param("airbyte-source-nonexisting", "0.1.0", "https://test.pypi.org/pypi", False, id="package not published on test.pypi"),
        pytest.param("airbyte-source-pokeapi", "0.2.0", "https://some-non-existing-host.com", False, id="host does not exist"),
    ],
)
def test_is_package_published(package_name, version, registry_url, expected):
    assert is_package_published(package_name, version, registry_url) == expected
