# `Auto merge`

## Purpose

This Python package is made to merge pull requests automatically on the Airbyte Repo. It is used in
the [following workflow](.github/workflows/auto_merge.yml).

A pull request is currently considered as auto-mergeable if:

- It has the `auto-merge` Github label
- It only modifies files in connector-related directories
- All the required checks have passed

We want to auto-merge a specific set of connector pull requests to simplify the connector updates in
the following use cases:

- Pull requests updating Python dependencies or the connector base image
- Community contributions when they've been reviewed and approved by our team but CI is still
  running: to avoid an extra review iteration just to check CI status.

## Install and usage

### Get a Github token

You need to create a Github token with the following permissions:

- Read access to the repository to list open pull requests and their statuses
- Write access to the repository to merge pull requests

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

The execution will set the `GITHUB_STEP_SUMMARY` env var with a markdown summary of the PRs that
have been merged.
