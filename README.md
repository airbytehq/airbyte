# Airbyte-Enterprise

This is the closed-source equivalent to [airbytehq/airbyte](https://github.com/airbytehq/airbyte).
Tools like gradle, airbyte-ci, etc. are expected to behave in exactly the same way.

## Development Setup

### Code Formatting

To format the code in this repository, run:

```shell
pre-commit run --all-files
```

#### Prerequisites

1. Install pre-commit (e.g., through Homebrew):
   ```shell
   brew install pre-commit
   ```

2. For Java code formatting, Maven is required:
   ```shell
   brew install maven
   ```

## Git Submodule Setup

This repo has `airbytehq/airbyte` as a submodule, located in `airbyte-submodule`,
and then a lot of symlinks pointing inside of there to make gradle and airbyte-ci magically work
just the same.

After cloning this repo, initialize the submodule with:

```shell
cd airbyte-enterprise
git submodule init
git submodule update --remote`
```

Then, simply never touch it.
Git submodules are a regular source of annoyance for developers of all kinds.

Should it happen that the submodule becomes _dirty_ because some file was changed unintentionally:

```shell
cd airbyte-submodule
git reset --hard
git clean -f -d
cd ..
```

Further reading on git submodules:

- https://www.cyberdemon.org/2024/03/20/submodules.html
- https://www.atlassian.com/git/tutorials/git-submodule
- https://git-scm.com/book/en/v2/Git-Tools-Submodules
- https://git-scm.com/docs/git-submodule

## Enterprise Connector Stubs

We're using a JSON file on GCS bucket as a set of minimal marketings stubs that show up in the catalog when the actual connectors are not available yet.

> [!warning]
> See `connector_stubs.json` for an example. This file is not automatically synced to the bucket.
> THIS FILE IS NOT AUTOMATICALLY SYNCED WITH PROD.
> THERE IS NO GUARANTEE IT'S UP TO DATE.
> [Here's the Notion guide on how it works](https://www.notion.so/Enterprise-Stubs-Catalog-34796e777cb34e16966639fa62ae1afc?pvs=4).

```shell

# Download the file
gsutil cp gs://prod-airbyte-cloud-connector-metadata-service/resources/connector_stubs/v1/connector_stubs.json ./connector_stubs.json

# do your thing

# Upload the file and pray for the best
gsutil cp ./connector_stubs.json gs://prod-airbyte-cloud-connector-metadata-service/resources/connector_stubs/v1/connector_stubs.json
```
