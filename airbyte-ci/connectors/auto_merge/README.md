# `auto_merge`

This python package is made to merge pull requests automatically on the Airbyte Repo. It is used in the [following workflow](TBD).

A pull request is currently considered as auto-mergeable if:
- It has the `auto-merge` label
- It is only touching files in connector related directories
- All the required checks have passed


## Install and usage
### Get a Github token
You need to create a Github token with the following permissions:
* Read access to the repository to list open pull requests and their statuses
* Write access to the repository to merge pull requests

### Local install and run
```
poetry install
export GITHUB_TOKEN=<your_github_token>
# By default no merge will be done, you need to set the AUTO_MERGE_PRODUCTION environment variable to true to actually merge the PRs
poetry run auto-merge
```

### In CI
```
export GITHUB_TOKEN=<your_github_token>
export AUTO_MERGE_PRODUCTION=true
poetry install
poetry run auto-merge
```

The execution will set the `GITHUB_STEP_SUMMARY` env var with a markdown summary of the PRs that have been merged.