# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import pytest
from airbyte_lib._util import github_pip_url, connector_pip_url

@pytest.mark.parametrize('owner, repo, branch_or_ref, package_name, subdirectory, expected', [
    ('airbytehq', 'airbyte', None, None, None, 'git+https://github.com/airbytehq/airbyte.git'),
    ('airbytehq', 'airbyte', 'master', None, None, 'git+https://github.com/airbytehq/airbyte.git@master'),
    ('airbytehq', 'airbyte', 'my-branch', None, None, 'git+https://github.com/airbytehq/airbyte.git@my-branch'),
    ('airbytehq', 'airbyte', 'my-branch', 'airbyte-lib', None, 'git+https://github.com/airbytehq/airbyte.git@my-branch#egg=airbyte-lib'),
    ('airbytehq', 'airbyte', 'my-branch', 'airbyte-lib', 'airbyte-lib', 'git+https://github.com/airbytehq/airbyte.git@my-branch#egg=airbyte-lib&subdirectory=airbyte-lib'),
])
def test_github_pip_url(owner, repo, branch_or_ref, package_name, subdirectory, expected):
    result = github_pip_url(owner, repo, branch_or_ref=branch_or_ref, package_name=package_name, subdirectory=subdirectory)
    assert result == expected

@pytest.mark.parametrize('connector_name, branch, owner, expected', [
    ('source-coin-api', 'my-branch', None, 'git+https://github.com/airbytehq/airbyte.git@my-branch#egg=source-coin-api&subdirectory=airbyte-integrations/connectors/source-coin-api'),
    ('source-coin-api', 'my-branch', 'my-fork', 'git+https://github.com/my-fork/airbyte.git@my-branch#egg=source-coin-api&subdirectory=airbyte-integrations/connectors/source-coin-api'),
])
def test_connector_pip_url(connector_name, branch, owner, expected):
    result = connector_pip_url(
        connector_name,
        branch,
        owner=owner)
    assert result == expected
