# Code formatting

## Tools

### 🐍 Python

We format our Python code using:

- [Black](https://github.com/psf/black) for code formatting
- [isort](https://pycqa.github.io/isort/) for import sorting

Our configuration for both tools is in the [pyproject.toml](https://github.com/airbytehq/airbyte/blob/master/pyproject.toml) file.

### ☕ Java

We format our Java code using [Spotless](https://github.com/diffplug/spotless).
Our configuration for Spotless is in the [spotless-maven-pom.xml](https://github.com/airbytehq/airbyte/blob/master/spotless-maven-pom.xml) file.

### Json and Yaml

We format our Json and Yaml files using [prettier](https://prettier.io/).

## Pre-push hooks and CI

We wrapped all our code formatting tools in [airbyte-ci](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md).

### Local formatting

You can run `airbyte-ci format fix all` to format all the code in the repository.
We wrapped this command in a pre-push hook so that you can't push code that is not formatted.

To install the pre-push hook, run:

```bash
make tools.pre-commit.setup
```

This will install `airbyte-ci` and the pre-push hook.

The pre-push hook runs formatting on all the repo files.
If the hook attempts to format a file that is not part of your contribution, it means that formatting is also broken in the master branch. Please open a separate PR to fix the formatting in the master branch.

### CI checks

In the CI we run the `airbyte-ci format check all` command to check that all the code is formatted.
If it is not, the CI will fail and you will have to run `airbyte-ci format fix all` locally to fix the formatting issues.
Failure on the CI is not expected if you installed the pre-push hook.
