# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import pytest
from airbyte_lib._util import github_pip_url

@pytest.mark.parametrize('owner, repo, branch_or_ref, package_name, subdirectory, expected', [
    ('airbytehq', 'airbyte', None, None, None, 'git+https://github.com/airbytehq/airbyte.git@master'),
    ('airbytehq', 'airbyte', 'my-branch', None, None, 'git+https://github.com/airbytehq/airbyte.git@my-branch'),
    ('airbytehq', 'airbyte', 'my-branch', 'airbyte-lib', None, 'git+https://github.com/airbytehq/airbyte.git@my-branch#egg=airbyte-lib'),
    ('airbytehq', 'airbyte', 'my-branch', 'airbyte-lib', 'airbyte-lib', 'git+https://github.com/airbytehq/airbyte.git@my-branch#egg=airbyte-lib#subdirectory=airbyte-lib'),
    ('airbytehq', 'other-repo', None, None, None, 'git+https://github.com/airbytehq/other-repo.git@main'),
])
def test_github_pip_url(owner, repo, branch_or_ref, package_name, subdirectory, expected):
    result = github_pip_url(owner, repo, branch_or_ref=branch_or_ref, package_name=package_name, subdirectory=subdirectory)
    assert result == expected
