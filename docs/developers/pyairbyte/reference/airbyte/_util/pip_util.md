---
sidebar_label: pip_util
title: airbyte._util.pip_util
---

Internal utility functions for dealing with pip.

## annotations

#### github\_pip\_url

```python
def github_pip_url(owner: str = "airbytehq",
                   repo: str = "airbyte",
                   *,
                   package_name: str,
                   branch_or_ref: str | None = None,
                   subdirectory: str | None = None) -> str
```

Return the pip URL for a GitHub repository.

Results will look like:
- `git+airbytehq/airbyte.git#egg=airbyte-lib&subdirectory=airbyte-lib'
- `git+airbytehq/airbyte.git@master#egg=airbyte-lib&amp;subdirectory=airbyte-lib&#x27;
- `git+airbytehq/airbyte.git@my-branch#egg=source-github
   &amp;subdirectory=airbyte-integrations/connectors/source-github&#x27;

#### connector\_pip\_url

```python
def connector_pip_url(connector_name: str,
                      branch: str,
                      *,
                      owner: str | None = None) -> str
```

Return a pip URL for a connector in the main `airbytehq/airbyte` git repo.

