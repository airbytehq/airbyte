# Airbyte CI CLI

## What is it?

`airbyte-ci` is a command line interface to run CI/CD pipelines. The goal of this CLI is to offer
developers a tool to run these pipelines locally and in a CI context with the same guarantee. It can
prevent unnecessary commit -> push cycles developers typically go through when they when to test
their changes against a remote CI. This is made possible thanks to the use of
[Dagger](https://dagger.io), a CI/CD engine relying on Docker Buildkit to provide reproducible
builds. Our pipeline are declared with Python code, the main entrypoint is
[here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connector_ops/connector_ops/pipelines/commands/airbyte_ci.py).
This documentation should be helpful for both local and CI use of the CLI. We indeed
[power connector testing in the CI with this CLI](https://github.com/airbytehq/airbyte/blob/master/.github/workflows/connector_integration_test_single_dagger.yml#L78).

## How to install

### Requirements

- A running Docker engine with version >= 20.10.23

## Install or Update

The recommended way to install `airbyte-ci` is using the [Makefile](../../../Makefile).

```sh
# from the root of the airbyte repository
make tools.airbyte-ci.install
```

### Setting up connector secrets access

If you plan to use Airbyte CI to run CAT (Connector Acceptance Tests), we recommend setting up GSM
access so that Airbyte CI can pull remote secrets from GSM. For setup instructions, see the CI
Credentials package (which Airbyte CI uses under the hood) README's
[Get GSM Access](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/ci_credentials/README.md#get-gsm-access)
instructions.

### Updating the airbyte-ci tool

To reinstall airbyte-ci, run the following command:

```sh
airbyte-ci update
```

or if that fails, you can reinstall it with the following command:

```sh
# from the root of the airbyte repository
make tools.airbyte-ci.install
```

## Checking the airbyte-ci install

To check that airbyte-ci is installed correctly, run the following command:

```sh
make tools.airbyte-ci.check
```

## Cleaning the airbyte-ci install

To clean the airbyte-ci install, run the following command:

```sh
make tools.airbyte-ci.clean
```

## Disabling telemetry

We collect anonymous usage data to help improve the tool. If you would like to disable this, you can set the `AIRBYTE_CI_DISABLE_TELEMETRY` environment variable to `true`.

## Installation for development

#### Pre-requisites

- Poetry >= 1.1.8
- Python >= 3.10

#### Installation

If you are developing on pipelines, we recommend installing airbyte-ci with poetry:

```bash
cd airbyte-ci/connectors/pipelines/
poetry install
poetry shell
cd ../../
```

**Alternatively**, you can install airbyte-ci with pipx so that the entrypoint is available in your
PATH:

```bash
make tools.airbyte-ci.install
```

However, this will not automatically install the dependencies for the local dependencies of
airbyte-ci, or respect the lockfile.

Its often best to use the `poetry` steps instead.

#### Running Tests

From `airbyte-ci/connectors/pipelines`:

```bash
poetry run pytest tests
```

You can also run a subset of tests:

```bash
poetry run pytest pipelines/models/steps.py
```

More options, such as running test by keyword matching, are available - see the
[pytest CLI documentation](https://docs.pytest.org/en/6.2.x/usage.html) for all the available
options.```

#### Checking Code Format (Pipelines)

```bash
poetry run ruff check pipelines
```

## Commands reference

At this point you can run `airbyte-ci` commands.

- [`airbyte-ci` command group](#airbyte-ci)
  - [Options](#options)
- [`connectors` command subgroup](#connectors-command-subgroup)
  - [Options](#options-1)
- [`connectors list` command](#connectors-list-command)
- [`connectors test` command](#connectors-test-command)
  - [Examples](#examples-)
  - [What it runs](#what-it-runs-)
- [`connectors build` command](#connectors-build-command)
  - [What it runs](#what-it-runs)
- [`connectors publish` command](#connectors-publish-command)
- [Examples](#examples)
- [Options](#options-2)
- [`connectors bump_version` command](#connectors-bump_version)
- [`connectors upgrade_cdk` command](#connectors-upgrade_cdk)
- [`connectors upgrade_base_image` command](#connectors-upgrade_base_image)
- [`connectors migrate_to_base_image` command](#connectors-migrate_to_base_image)
- [`format` command subgroup](#format-subgroup)
  - [`format check` command](#format-check-command)
  - [`format fix` command](#format-fix-command)
- [`metadata` command subgroup](#metadata-command-subgroup)
- [`metadata validate` command](#metadata-validate-command)
  - [Example](#example)
  - [Options](#options-3)
- [`metadata upload` command](#metadata-upload-command)
  - [Example](#example-1)
  - [Options](#options-4)
- [`metadata deploy orchestrator` command](#metadata-deploy-orchestrator-command)
  - [Example](#example-2)
  - [What it runs](#what-it-runs--1)
- [`metadata test lib` command](#metadata-test-lib-command)
  - [Example](#example-3)
- [`metadata test orchestrator` command](#metadata-test-orchestrator-command)
  - [Example](#example-4)
- [`tests` command](#test-command)
  - [Example](#example-5)

### <a id="airbyte-ci-command-group"></a>`airbyte-ci` command group

**The main command group option has sensible defaults. In local use cases you're not likely to pass
options to the `airbyte-ci` command group.**

#### Options

| Option                                         | Default value                   | Mapped environment variable   | Description                                                                                 |
| ---------------------------------------------- | ------------------------------- | ----------------------------- | ------------------------------------------------------------------------------------------- |
| `--yes/--y`                                    | False                           |                               | Agrees to all prompts.                                                                      |
| `--yes-auto-update`                            | False                           |                               | Agrees to the auto update prompts.                                                          |
| `--enable-update-check/--disable-update-check` | True                            |                               | Turns on the update check feature                                                           |
| `--enable-dagger-run/--disable-dagger-run`     | `--enable-dagger-run`           |                               | Disables the Dagger terminal UI.                                                            |
| `--is-local/--is-ci`                           | `--is-local`                    |                               | Determines the environment in which the CLI runs: local environment or CI environment.      |
| `--git-branch`                                 | The checked out git branch name | `CI_GIT_BRANCH`               | The git branch on which the pipelines will run.                                             |
| `--git-revision`                               | The current branch head         | `CI_GIT_REVISION`             | The commit hash on which the pipelines will run.                                            |
| `--diffed-branch`                              | `origin/master`                 |                               | Branch to which the git diff will happen to detect new or modified files.                   |
| `--gha-workflow-run-id`                        |                                 |                               | GHA CI only - The run id of the GitHub action workflow                                      |
| `--ci-context`                                 | `manual`                        |                               | The current CI context: `manual` for manual run, `pull_request`, `nightly_builds`, `master` |
| `--pipeline-start-timestamp`                   | Current epoch time              | `CI_PIPELINE_START_TIMESTAMP` | Start time of the pipeline as epoch time. Used for pipeline run duration computation.       |
| `--show-dagger-logs/--hide-dagger-logs`        | `--hide-dagger-logs`            |                               | Flag to show or hide the dagger logs.                                                       |

### <a id="connectors-command-subgroup"></a>`connectors` command subgroup

Available commands:

- `airbyte-ci connectors test`: Run tests for one or multiple connectors.
- `airbyte-ci connectors build`: Build docker images for one or multiple connectors.
- `airbyte-ci connectors publish`: Publish a connector to Airbyte's DockerHub.

#### Options

| Option                                                         | Multiple | Default value                    | Mapped Environment Variable | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| -------------------------------------------------------------- | -------- | -------------------------------- | --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--use-remote-secrets/--use-local-secrets`                     | False    |                                  |                             | If --use-remote-secrets, connectors configuration will be pulled from Google Secret Manager. Requires the `GCP_GSM_CREDENTIALS` environment variable to be set with a service account with permission to read GSM secrets. If --use-local-secrets the connector configuration will be read from the local connector `secrets` folder. If this flag is not used and a `GCP_GSM_CREDENTIALS` environment variable is set remote secrets will be used, local secrets will be used otherwise. |
| `--name`                                                       | True     |                                  |                             | Select a specific connector for which the pipeline will run. Can be used multiple times to select multiple connectors. The expected name is the connector technical name. e.g. `source-pokeapi`                                                                                                                                                                                                                                                                                           |
| `--support-level`                                              | True     |                                  |                             | Select connectors with a specific support level: `community`, `certified`. Can be used multiple times to select multiple support levels.                                                                                                                                                                                                                                                                                                                                                  |
| `--metadata-query`                                             | False    |                                  |                             | Filter connectors by the `data` field in the metadata file using a [simpleeval](https://github.com/danthedeckie/simpleeval) query. e.g. 'data.ab_internal.ql == 200'                                                                                                                                                                                                                                                                                                                      |
| `--use-local-cdk`                                              | False    | False                            |                             | Build with the airbyte-cdk from the local repository. " "This is useful for testing changes to the CDK.                                                                                                                                                                                                                                                                                                                                                                                   |
| `--language`                                                   | True     |                                  |                             | Select connectors with a specific language: `python`, `low-code`, `java`. Can be used multiple times to select multiple languages.                                                                                                                                                                                                                                                                                                                                                        |
| `--modified`                                                   | False    | False                            |                             | Run the pipeline on only the modified connectors on the branch or previous commit (depends on the pipeline implementation).                                                                                                                                                                                                                                                                                                                                                               |
| `--concurrency`                                                | False    | 5                                |                             | Control the number of connector pipelines that can run in parallel. Useful to speed up pipelines or control their resource usage.                                                                                                                                                                                                                                                                                                                                                         |
| `--metadata-change-only/--not-metadata-change-only`            | False    | `--not-metadata-change-only`     |                             | Only run the pipeline on connectors with changes on their metadata.yaml file.                                                                                                                                                                                                                                                                                                                                                                                                             |
| `--enable-dependency-scanning / --disable-dependency-scanning` | False    | ` --disable-dependency-scanning` |                             | When enabled the dependency scanning will be performed to detect the connectors to select according to a dependency change.                                                                                                                                                                                                                                                                                                                                                               |
| `--docker-hub-username`                                        |          |                                  | DOCKER_HUB_USERNAME         | Your username to connect to DockerHub. Required for the publish subcommand.                                                                                                                                                                                                                                                                                                                                                                                                               |
| `--docker-hub-password`                                        |          |                                  | DOCKER_HUB_PASSWORD         | Your password to connect to DockerHub. Required for the publish subcommand.                                                                                                                                                                                                                                                                                                                                                                                                               |

### <a id="connectors-list-command"></a>`connectors list` command

Retrieve the list of connectors satisfying the provided filters.

#### Examples

List all connectors:

`airbyte-ci connectors list`

List certified connectors:

`airbyte-ci connectors --support-level=certified list`

List connectors changed on the current branch:

`airbyte-ci connectors --modified list`

List connectors with a specific language:

`airbyte-ci connectors --language=python list`

List connectors with multiple filters:

`airbyte-ci connectors --language=low-code --support-level=certified list`

### <a id="connectors-test-command"></a>`connectors test` command

Run a test pipeline for one or multiple connectors.

#### Examples

Test a single connector: `airbyte-ci connectors --name=source-pokeapi test`

Test multiple connectors: `airbyte-ci connectors --name=source-pokeapi --name=source-bigquery test`

Test certified connectors: `airbyte-ci connectors --support-level=certified test`

Test connectors changed on the current branch: `airbyte-ci connectors --modified test`

Run acceptance test only on the modified connectors, just run its full refresh tests:
`airbyte-ci connectors --modified test --only-step="acceptance" --acceptance.-k=test_full_refresh`

#### What it runs

```mermaid
flowchart TD
    entrypoint[[For each selected connector]]
    subgraph static ["Static code analysis"]
      qa[Run QA checks]
      sem["Check version follows semantic versionning"]
      incr["Check version is incremented"]
      metadata_validation["Run metadata validation on metadata.yaml"]
      sem --> incr
    end
    subgraph tests ["Tests"]
        build[Build connector docker image]
        unit[Run unit tests]
        integration[Run integration tests]
        airbyte_lib_validation[Run airbyte-lib validation tests]
        cat[Run connector acceptance tests]
        secret[Load connector configuration]

        unit-->secret
        unit-->build
        secret-->integration
        secret-->cat
        secret-->airbyte_lib_validation
        build-->integration
        build-->cat
    end
    entrypoint-->static
    entrypoint-->tests
    report["Build test report"]
    tests-->report
    static-->report
```

#### Options

| Option                                                  | Multiple | Default value | Description                                                                                                                                                                                              |
| ------------------------------------------------------- | -------- | ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--skip-step/-x`                                        | True     |               | Skip steps by id e.g. `-x unit -x acceptance`                                                                                                                                                            |
| `--only-step/-k`                                        | True     |               | Only run specific steps by id e.g. `-k unit -k acceptance`                                                                                                                                               |
| `--fail-fast`                                           | False    | False         | Abort after any tests fail, rather than continuing to run additional tests. Use this setting to confirm a known bug is fixed (or not), or when you only require a pass/fail result.                      |
| `--code-tests-only`                                     | True     | False         | Skip any tests not directly related to code updates. For instance, metadata checks, version bump checks, changelog verification, etc. Use this setting to help focus on code quality during development. |
| `--concurrent-cat`                                      | False    | False         | Make CAT tests run concurrently using pytest-xdist. Be careful about source or destination API rate limits.                                                                                              |
| `--<step-id>.<extra-parameter>=<extra-parameter-value>` | True     |               | You can pass extra parameters for specific test steps. More details in the extra parameters section below                                                                                                |
| `--ci-requirements`                                     | False    |               |                                                                                                                                                                                                          | Output the CI requirements as a JSON payload. It is used to determine the CI runner to use.

Note:

- The above options are implemented for Java connectors but may not be available for Python
  connectors. If an option is not supported, the pipeline will not fail but instead the 'default'
  behavior will be executed.

#### Extra parameters

You can pass extra parameters to the following steps:

- `unit`
- `integration`
- `acceptance`

This allows you to override the default parameters of these steps. For example, you can only run the
`test_read` test of the acceptance test suite with:
`airbyte-ci connectors --name=source-pokeapi test --acceptance.-k=test_read` Here the `-k` parameter
is passed to the pytest command running acceptance tests. Please keep in mind that the extra
parameters are not validated by the CLI: if you pass an invalid parameter, you'll face a late
failure during the pipeline execution.

### <a id="connectors-build-command"></a>`connectors build` command

Run a build pipeline for one or multiple connectors and export the built docker image to the local
docker host. It's mainly purposed for local use.

Build a single connector: `airbyte-ci connectors --name=source-pokeapi build`

Build a single connector with a custom image tag:
`airbyte-ci connectors --name=source-pokeapi build --tag=my-custom-tag`

Build a single connector for multiple architectures:
`airbyte-ci connectors --name=source-pokeapi build --architecture=linux/amd64 --architecture=linux/arm64`

You will get:

- `airbyte/source-pokeapi:dev-linux-amd64`
- `airbyte/source-pokeapi:dev-linux-arm64`

Build multiple connectors:
`airbyte-ci connectors --name=source-pokeapi --name=source-bigquery build`

Build certified connectors: `airbyte-ci connectors --support-level=certified build`

Build connectors changed on the current branch: `airbyte-ci connectors --modified build`

#### What it runs

For Python and Low Code connectors:

```mermaid
flowchart TD
    arch(For each platform amd64/arm64)
    connector[Build connector image]
    load[Load to docker host with :dev tag, current platform]
    spec[Get spec]
    arch-->connector-->spec--"if success"-->load
```

For Java connectors:

```mermaid
flowchart TD
    arch(For each platform amd64/arm64)
    distTar[Gradle distTar task run]
    base[Build integration base]
    java_base[Build integration base Java]
    normalization[Build Normalization]
    connector[Build connector image]

    arch-->base-->java_base-->connector
    distTar-->connector
    normalization--"if supports normalization"-->connector

    load[Load to docker host with :dev tag]
    spec[Get spec]
    connector-->spec--"if success"-->load
```

### Options

| Option                | Multiple | Default value  | Description                                                          |
| --------------------- | -------- | -------------- | -------------------------------------------------------------------- |
| `--architecture`/`-a` | True     | Local platform | Defines for which architecture(s) the connector image will be built. |
| `--tag`               | False    | `dev`          | Image tag for the built image.                                       |

### <a id="connectors-publish-command"></a>`connectors publish` command

Run a publish pipeline for one or multiple connectors. It's mainly purposed for CI use to release a
connector update.

### Examples

Publish all connectors modified in the head commit: `airbyte-ci connectors --modified publish`

### Options

| Option                               | Required | Default                         | Mapped environment variable        | Description                                                                                                                                                                               |
| ------------------------------------ | -------- | ------------------------------- | ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--pre-release/--main-release`       | False    | `--pre-release`                 |                                    | Whether to publish the pre-release or the main release version of a connector. Defaults to pre-release. For main release you have to set the credentials to interact with the GCS bucket. |
| `--spec-cache-gcs-credentials`       | False    |                                 | `SPEC_CACHE_GCS_CREDENTIALS`       | The service account key to upload files to the GCS bucket hosting spec cache.                                                                                                             |
| `--spec-cache-bucket-name`           | False    |                                 | `SPEC_CACHE_BUCKET_NAME`           | The name of the GCS bucket where specs will be cached.                                                                                                                                    |
| `--metadata-service-gcs-credentials` | False    |                                 | `METADATA_SERVICE_GCS_CREDENTIALS` | The service account key to upload files to the GCS bucket hosting the metadata files.                                                                                                     |
| `--metadata-service-bucket-name`     | False    |                                 | `METADATA_SERVICE_BUCKET_NAME`     | The name of the GCS bucket where metadata files will be uploaded.                                                                                                                         |
| `--slack-webhook`                    | False    |                                 | `SLACK_WEBHOOK`                    | The Slack webhook URL to send notifications to.                                                                                                                                           |
| `--slack-channel`                    | False    |                                 | `SLACK_CHANNEL`                    | The Slack channel name to send notifications to.                                                                                                                                          |
| `--ci-requirements`                  | False    |                                 |                                    | Output the CI requirements as a JSON payload. It is used to determine the CI runner to use.                                                                                               |
| `--python-registry-token`            | False    |                                 | `PYTHON_REGISTRY_TOKEN`            | The API token to authenticate with the registry. For pypi, the `pypi-` prefix needs to be specified                                                                                       |
| `--python-registry-url`              | False    | https://upload.pypi.org/legacy/ | `PYTHON_REGISTRY_URL`              | The python registry to publish to. Defaults to main pypi                                                                                                                                  |
| `--python-registry-check-url`        | False    | https://pypi.org/pypi           | `PYTHON_REGISTRY_CHECK_URL`        | The python registry url to check whether a package is published already                                                                                                                   |

I've added an empty "Default" column, and you can fill in the default values as needed.

#### What it runs

```mermaid
flowchart TD
    validate[Validate the metadata file]
    check[Check if the connector image already exists]
    build[Build the connector image for all platform variants]
    publish_to_python_registry[Push the connector image to the python registry if enabled]
    upload_spec[Upload connector spec to the spec cache bucket]
    push[Push the connector image from DockerHub, with platform variants]
    pull[Pull the connector image from DockerHub to check SPEC can be run and the image layers are healthy]
    upload_metadata[Upload its metadata file to the metadata service bucket]

    validate-->check-->build-->upload_spec-->publish_to_python_registry-->push-->pull-->upload_metadata
```

#### Python registry publishing

If `remoteRegistries.pypi.enabled` in the connector metadata is set to `true`, the connector will be
published to the python registry. To do so, the `--python-registry-token` and
`--python-registry-url` options are used to authenticate with the registry and publish the
connector. If the current version of the connector is already published to the registry, the publish
will be skipped (the `--python-registry-check-url` is used for the check).

On a pre-release, the connector will be published as a `.dev<N>` version.

The `remoteRegistries.pypi.packageName` field holds the name of the used package name. It should be
set to `airbyte-source-<package name>`. Certified Python connectors are required to have PyPI
publishing enabled.

An example `remoteRegistries` entry in a connector `metadata.yaml` looks like this:

```yaml
remoteRegistries:
  pypi:
    enabled: true
    packageName: airbyte-source-pokeapi
```

### <a id="connectors-bump_version"></a>`connectors bump_version` command

Bump the version of the selected connectors.

### Examples

Bump source-openweather:
`airbyte-ci connectors --name=source-openweather bump_version patch <pr-number> "<changelog-entry>"`

#### Arguments

| Argument              | Description                                                            |
| --------------------- | ---------------------------------------------------------------------- |
| `BUMP_TYPE`           | major, minor or patch                                                  |
| `PULL_REQUEST_NUMBER` | The GitHub pull request number, used in the changelog entry            |
| `CHANGELOG_ENTRY`     | The changelog entry that will get added to the connector documentation |

### <a id="connectors-upgrade_cdk"></a>`connectors upgrade_cdk` command

Upgrade the CDK version of the selected connectors by updating the dependency in the setup.py file.

### Examples

Upgrade for source-openweather:
`airbyte-ci connectors --name=source-openweather upgrade_cdk <new-cdk-version>`

#### Arguments

| Argument      | Description                                             |
| ------------- | ------------------------------------------------------- |
| `CDK_VERSION` | CDK version to set (default to the most recent version) |

### <a id="connectors-upgrade_base_image"></a>`connectors upgrade_base_image` command

Modify the selected connector metadata to use the latest base image version.

### Examples

Upgrade the base image for source-openweather:
`airbyte-ci connectors --name=source-openweather upgrade_base_image`

### Options

| Option                  | Required | Default | Mapped environment variable | Description                                                                                                     |
| ----------------------- | -------- | ------- | --------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `--docker-hub-username` | True     |         | `DOCKER_HUB_USERNAME`       | Your username to connect to DockerHub. It's used to read the base image registry.                               |
| `--docker-hub-password` | True     |         | `DOCKER_HUB_PASSWORD`       | Your password to connect to DockerHub. It's used to read the base image registry.                               |
| `--set-if-not-exists`   | False    | True    |                             | Whether to set or not the baseImage metadata if no connectorBuildOptions is declared in the connector metadata. |

### <a id="connectors-migrate_to_base_image"></a>`connectors migrate_to_base_image` command

Make a connector using a Dockerfile migrate to the base image by:

- Removing its Dockerfile
- Updating its metadata to use the latest base image version
- Updating its documentation to explain the build process
- Bumping by a patch version

### Examples

Migrate source-openweather to use the base image:
`airbyte-ci connectors --name=source-openweather migrate_to_base_image`

### Arguments

| Argument              | Description                                                 |
| --------------------- | ----------------------------------------------------------- |
| `PULL_REQUEST_NUMBER` | The GitHub pull request number, used in the changelog entry |

### <a id="format-subgroup"></a>`format` command subgroup

Available commands:

- `airbyte-ci format check all`
- `airbyte-ci format fix all`

### Options

| Option              | Required | Default | Mapped environment variable | Description                                                                                 |
| ------------------- | -------- | ------- | --------------------------- | ------------------------------------------------------------------------------------------- |
| `--quiet/-q`        | False    | False   |                             | Hide formatter execution details in reporting.                                              |
| `--ci-requirements` | False    |         |                             | Output the CI requirements as a JSON payload. It is used to determine the CI runner to use. |

### Examples

- Check for formatting errors in the repository: `airbyte-ci format check all`
- Fix formatting for only python files: `airbyte-ci format fix python`

### <a id="format-check-command"></a>`format check all` command

This command runs formatting checks, but does not format the code in place. It will exit 1 as soon
as a failure is encountered. To fix errors, use `airbyte-ci format fix all`.

Running `airbyte-ci format check` will run checks on all different types of code. Run
`airbyte-ci format check --help` for subcommands to check formatting for only certain types of
files.

### <a id="format-fix-command"></a>`format fix all` command

This command runs formatting checks and reformats any code that would be reformatted, so it's
recommended to stage changes you might have before running this command.

Running `airbyte-ci format fix all` will format all of the different types of code. Run
`airbyte-ci format fix --help` for subcommands to format only certain types of files.

### <a id="poetry-subgroup"></a>`poetry` command subgroup

Available commands:

- `airbyte-ci poetry publish`

### Options

| Option           | Required | Default | Mapped environment variable | Description                                                    |
| ---------------- | -------- | ------- | --------------------------- | -------------------------------------------------------------- |
| `--package-path` | True     |         |                             | The path to the python package to execute a poetry command on. |

### Examples

- Publish a python package:
  `airbyte-ci poetry --package-path=path/to/package publish --publish-name=my-package --publish-version="1.2.3" --python-registry-token="..." --registry-url="http://host.docker.internal:8012/"`

### <a id="format-check-command"></a>`publish` command

This command publishes poetry packages (using `pyproject.toml`) or python packages (using
`setup.py`) to a python registry.

For poetry packages, the package name and version can be taken from the `pyproject.toml` file or be
specified as options.

#### Options

| Option                    | Required | Default                         | Mapped environment variable | Description                                                                                              |
| ------------------------- | -------- | ------------------------------- | --------------------------- | -------------------------------------------------------------------------------------------------------- |
| `--publish-name`          | False    |                                 |                             | The name of the package. Not required for poetry packages that define it in the `pyproject.toml` file    |
| `--publish-version`       | False    |                                 |                             | The version of the package. Not required for poetry packages that define it in the `pyproject.toml` file |
| `--python-registry-token` | True     |                                 | PYTHON_REGISTRY_TOKEN       | The API token to authenticate with the registry. For pypi, the `pypi-` prefix needs to be specified      |
| `--python-registry-url`   | False    | https://upload.pypi.org/legacy/ | PYTHON_REGISTRY_URL         | The python registry to publish to. Defaults to main pypi                                                 |

### <a id="metadata-validate-command-subgroup"></a>`metadata` command subgroup

Available commands:

- `airbyte-ci metadata deploy orchestrator`

### <a id="metadata-upload-orchestrator"></a>`metadata deploy orchestrator` command

This command deploys the metadata service orchestrator to production. The
`DAGSTER_CLOUD_METADATA_API_TOKEN` environment variable must be set.

#### Example

`airbyte-ci metadata deploy orchestrator`

#### What it runs

```mermaid
flowchart TD
    test[Run orchestrator tests] --> deploy[Deploy orchestrator to Dagster Cloud]
```

### <a id="tests-command"></a>`tests` command

This command runs the poe tasks declared in the `[tool.airbyte-ci]` section of our internal poetry packages.
Feel free to checkout this [Pydantic model](https://github.com/airbytehq/airbyte/blob/main/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/test/models.py#L9) to see the list of available options in `[tool.airbyte-ci]` section.

You can find the list of internal packages [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/test/__init__.py#L1)

#### Options

| Option                     | Required | Multiple | Description                                                                                 |
| -------------------------- | -------- | -------- | ------------------------------------------------------------------------------------------- |
| `--poetry-package-path/-p` | False    | True     | Poetry packages path to run the poe tasks for.                                              |
| `--modified`               | False    | False    | Run poe tasks of modified internal poetry packages.                                         |
| `--ci-requirements`        | False    | False    | Output the CI requirements as a JSON payload. It is used to determine the CI runner to use. |

#### Examples
You can pass multiple `--poetry-package-path` options to run poe tasks.

E.G.: running Poe tasks on `airbyte-lib` and `airbyte-ci/connectors/pipelines`:
`airbyte-ci test --poetry-package-path=airbyte-ci/connectors/pipelines --poetry-package-path=airbyte-lib`

E.G.: running Poe tasks on the modified internal packages of the current branch:
`airbyte-ci test --modified`


## Changelog

| Version | PR                                                         | Description                                                                                                                |
| ------- | ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| 4.4.0   | [#35317](https://github.com/airbytehq/airbyte/pull/35317)  | Augment java connector reports to include full logs and junit test results                                                 |
| 4.3.2   | [#35536](https://github.com/airbytehq/airbyte/pull/35536)  | Make QA checks run correctly on `*-strict-encrypt` connectors.                                                             |
| 4.3.1   | [#35437](https://github.com/airbytehq/airbyte/pull/35437)  | Do not run QA checks on publish, just MetadataValidation.                                                             |
| 4.3.0   | [#35438](https://github.com/airbytehq/airbyte/pull/35438)  | Optionally disable telemetry with environment variable.                                                                    |
| 4.2.4   | [#35325](https://github.com/airbytehq/airbyte/pull/35325)  | Use `connectors_qa` for QA checks and remove redundant checks.                                                             |
| 4.2.3   | [#35322](https://github.com/airbytehq/airbyte/pull/35322)  | Declare `connectors_qa` as an internal package for testing.                                                                |
| 4.2.2   | [#35364](https://github.com/airbytehq/airbyte/pull/35364)  | Fix connector tests following gradle changes in #35307.                                                                    |
| 4.2.1   | [#35204](https://github.com/airbytehq/airbyte/pull/35204)  | Run `poetry check` before `poetry install` on poetry package install.                                                      |
| 4.2.0   | [#35103](https://github.com/airbytehq/airbyte/pull/35103)  | Java 21 support.                                                                                                           |
| 4.1.4   | [#35039](https://github.com/airbytehq/airbyte/pull/35039)  | Fix bug which prevented gradle test reports from being added.                                                              |
| 4.1.3   | [#35010](https://github.com/airbytehq/airbyte/pull/35010)  | Use `poetry install --no-root` in the builder container.                                                                   |
| 4.1.2   | [#34945](https://github.com/airbytehq/airbyte/pull/34945)  | Only install main dependencies when running poetry install.                                                                |
| 4.1.1   | [#34430](https://github.com/airbytehq/airbyte/pull/34430)  | Speed up airbyte-ci startup (and airbyte-ci format).                                                                       |
| 4.1.0   | [#34923](https://github.com/airbytehq/airbyte/pull/34923)  | Include gradle test reports in HTML connector test report.                                                                 |
| 4.0.0   | [#34736](https://github.com/airbytehq/airbyte/pull/34736)  | Run poe tasks declared in internal poetry packages.                                                                        |
| 3.10.4  | [#34867](https://github.com/airbytehq/airbyte/pull/34867)  | Remove connector ops team                                                                                                  |
| 3.10.3  | [#34836](https://github.com/airbytehq/airbyte/pull/34836)  | Add check for python registry publishing enabled for certified python sources.                                             |
| 3.10.2  | [#34044](https://github.com/airbytehq/airbyte/pull/34044)  | Add pypi validation testing.                                                                                               |
| 3.10.1  | [#34756](https://github.com/airbytehq/airbyte/pull/34756)  | Enable connectors tests in draft PRs.                                                                                      |
| 3.10.0  | [#34606](https://github.com/airbytehq/airbyte/pull/34606)  | Allow configuration of separate check URL to check whether package exists already.                                         |
| 3.9.0   | [#34606](https://github.com/airbytehq/airbyte/pull/34606)  | Allow configuration of python registry URL via environment variable.                                                       |
| 3.8.1   | [#34607](https://github.com/airbytehq/airbyte/pull/34607)  | Improve gradle dependency cache volume protection.                                                                         |
| 3.8.0   | [#34316](https://github.com/airbytehq/airbyte/pull/34316)  | Expose Dagger engine image name in `--ci-requirements` and add `--ci-requirements` to the `airbyte-ci` root command group. |
| 3.7.3   | [#34560](https://github.com/airbytehq/airbyte/pull/34560)  | Simplify Gradle task execution framework by removing local maven repo support.                                             |
| 3.7.2   | [#34555](https://github.com/airbytehq/airbyte/pull/34555)  | Override secret masking in some very specific special cases.                                                               |
| 3.7.1   | [#34441](https://github.com/airbytehq/airbyte/pull/34441)  | Support masked secret scrubbing for java CDK v0.15+                                                                        |
| 3.7.0   | [#34343](https://github.com/airbytehq/airbyte/pull/34343)  | allow running connector upgrade_cdk for java connectors                                                                    |
| 3.6.1   | [#34490](https://github.com/airbytehq/airbyte/pull/34490)  | Fix inconsistent dagger log path typing                                                                                    |
| 3.6.0   | [#34111](https://github.com/airbytehq/airbyte/pull/34111)  | Add python registry publishing                                                                                             |
| 3.5.3   | [#34339](https://github.com/airbytehq/airbyte/pull/34339)  | only do minimal changes on a connector version_bump                                                                        |
| 3.5.2   | [#34381](https://github.com/airbytehq/airbyte/pull/34381)  | Bind a sidecar docker host for `airbyte-ci test`                                                                           |
| 3.5.1   | [#34321](https://github.com/airbytehq/airbyte/pull/34321)  | Upgrade to Dagger 0.9.6 .                                                                                                  |
| 3.5.0   | [#33313](https://github.com/airbytehq/airbyte/pull/33313)  | Pass extra params after Gradle tasks.                                                                                      |
| 3.4.2   | [#34301](https://github.com/airbytehq/airbyte/pull/34301)  | Pass extra params after Gradle tasks.                                                                                      |
| 3.4.1   | [#34067](https://github.com/airbytehq/airbyte/pull/34067)  | Use dagster-cloud 1.5.7 for deploy                                                                                         |
| 3.4.0   | [#34276](https://github.com/airbytehq/airbyte/pull/34276)  | Introduce `--only-step` option for connector tests.                                                                        |
| 3.3.0   | [#34218](https://github.com/airbytehq/airbyte/pull/34218)  | Introduce `--ci-requirements` option for client defined CI runners.                                                        |
| 3.2.0   | [#34050](https://github.com/airbytehq/airbyte/pull/34050)  | Connector test steps can take extra parameters                                                                             |
| 3.1.3   | [#34136](https://github.com/airbytehq/airbyte/pull/34136)  | Fix issue where dagger excludes were not being properly applied                                                            |
| 3.1.2   | [#33972](https://github.com/airbytehq/airbyte/pull/33972)  | Remove secrets scrubbing hack for --is-local and other small tweaks.                                                       |
| 3.1.1   | [#33979](https://github.com/airbytehq/airbyte/pull/33979)  | Fix AssertionError on report existence again                                                                               |
| 3.1.0   | [#33994](https://github.com/airbytehq/airbyte/pull/33994)  | Log more context information in CI.                                                                                        |
| 3.0.2   | [#33987](https://github.com/airbytehq/airbyte/pull/33987)  | Fix type checking issue when running --help                                                                                |
| 3.0.1   | [#33981](https://github.com/airbytehq/airbyte/pull/33981)  | Fix issues with deploying dagster, pin pendulum version in dagster-cli install                                             |
| 3.0.0   | [#33582](https://github.com/airbytehq/airbyte/pull/33582)  | Upgrade to Dagger 0.9.5                                                                                                    |
| 2.14.3  | [#33964](https://github.com/airbytehq/airbyte/pull/33964)  | Reintroduce mypy with fixes for AssertionError on publish and missing report URL on connector test commit status.          |
| 2.14.2  | [#33954](https://github.com/airbytehq/airbyte/pull/33954)  | Revert mypy changes                                                                                                        |
| 2.14.1  | [#33956](https://github.com/airbytehq/airbyte/pull/33956)  | Exclude pnpm lock files from auto-formatting                                                                               |
| 2.14.0  | [#33941](https://github.com/airbytehq/airbyte/pull/33941)  | Enable in-connector normalization in destination-postgres                                                                  |
| 2.13.1  | [#33920](https://github.com/airbytehq/airbyte/pull/33920)  | Report different sentry environments                                                                                       |
| 2.13.0  | [#33784](https://github.com/airbytehq/airbyte/pull/33784)  | Make `airbyte-ci test` able to run any poetry command                                                                      |
| 2.12.0  | [#33313](https://github.com/airbytehq/airbyte/pull/33313)  | Add upgrade CDK command                                                                                                    |
| 2.11.0  | [#32188](https://github.com/airbytehq/airbyte/pull/32188)  | Add -x option to connector test to allow for skipping steps                                                                |
| 2.10.12 | [#33419](https://github.com/airbytehq/airbyte/pull/33419)  | Make ClickPipelineContext handle dagger logging.                                                                           |
| 2.10.11 | [#33497](https://github.com/airbytehq/airbyte/pull/33497)  | Consider nested .gitignore rules in format.                                                                                |
| 2.10.10 | [#33449](https://github.com/airbytehq/airbyte/pull/33449)  | Add generated metadata models to the default format ignore list.                                                           |
| 2.10.9  | [#33370](https://github.com/airbytehq/airbyte/pull/33370)  | Fix bug that broke airbyte-ci test                                                                                         |
| 2.10.8  | [#33249](https://github.com/airbytehq/airbyte/pull/33249)  | Exclude git ignored files from formatting.                                                                                 |
| 2.10.7  | [#33248](https://github.com/airbytehq/airbyte/pull/33248)  | Fix bug which broke airbyte-ci connectors tests when optional DockerHub credentials env vars are not set.                  |
| 2.10.6  | [#33170](https://github.com/airbytehq/airbyte/pull/33170)  | Remove Dagger logs from console output of `format`.                                                                        |
| 2.10.5  | [#33097](https://github.com/airbytehq/airbyte/pull/33097)  | Improve `format` performances, exit with 1 status code when `fix` changes files.                                           |
| 2.10.4  | [#33206](https://github.com/airbytehq/airbyte/pull/33206)  | Add "-y/--yes" Flag to allow preconfirmation of prompts                                                                    |
| 2.10.3  | [#33080](https://github.com/airbytehq/airbyte/pull/33080)  | Fix update failing due to SSL error on install.                                                                            |
| 2.10.2  | [#33008](https://github.com/airbytehq/airbyte/pull/33008)  | Fix local `connector build`.                                                                                               |
| 2.10.1  | [#32928](https://github.com/airbytehq/airbyte/pull/32928)  | Fix BuildConnectorImages constructor.                                                                                      |
| 2.10.0  | [#32819](https://github.com/airbytehq/airbyte/pull/32819)  | Add `--tag` option to connector build.                                                                                     |
| 2.9.0   | [#32816](https://github.com/airbytehq/airbyte/pull/32816)  | Add `--architecture` option to connector build.                                                                            |
| 2.8.1   | [#32999](https://github.com/airbytehq/airbyte/pull/32999)  | Improve Java code formatting speed                                                                                         |
| 2.8.0   | [#31930](https://github.com/airbytehq/airbyte/pull/31930)  | Move pipx install to `airbyte-ci-dev`, and add auto-update feature targeting binary                                        |
| 2.7.3   | [#32847](https://github.com/airbytehq/airbyte/pull/32847)  | Improve --modified behaviour for pull requests.                                                                            |
| 2.7.2   | [#32839](https://github.com/airbytehq/airbyte/pull/32839)  | Revert changes in v2.7.1.                                                                                                  |
| 2.7.1   | [#32806](https://github.com/airbytehq/airbyte/pull/32806)  | Improve --modified behaviour for pull requests.                                                                            |
| 2.7.0   | [#31930](https://github.com/airbytehq/airbyte/pull/31930)  | Merge airbyte-ci-internal into airbyte-ci                                                                                  |
| 2.6.0   | [#31831](https://github.com/airbytehq/airbyte/pull/31831)  | Add `airbyte-ci format` commands, remove connector-specific formatting check                                               |
| 2.5.9   | [#32427](https://github.com/airbytehq/airbyte/pull/32427)  | Re-enable caching for source-postgres                                                                                      |
| 2.5.8   | [#32402](https://github.com/airbytehq/airbyte/pull/32402)  | Set Dagger Cloud token for airbyters only                                                                                  |
| 2.5.7   | [#31628](https://github.com/airbytehq/airbyte/pull/31628)  | Add ClickPipelineContext class                                                                                             |
| 2.5.6   | [#32139](https://github.com/airbytehq/airbyte/pull/32139)  | Test coverage report on Python connector UnitTest.                                                                         |
| 2.5.5   | [#32114](https://github.com/airbytehq/airbyte/pull/32114)  | Create cache mount for `/var/lib/docker` to store images in `dind` context.                                                |
| 2.5.4   | [#32090](https://github.com/airbytehq/airbyte/pull/32090)  | Do not cache `docker login`.                                                                                               |
| 2.5.3   | [#31974](https://github.com/airbytehq/airbyte/pull/31974)  | Fix latest CDK install and pip cache mount on connector install.                                                           |
| 2.5.2   | [#31871](https://github.com/airbytehq/airbyte/pull/31871)  | Deactivate PR comments, add HTML report links to the PR status when its ready.                                             |
| 2.5.1   | [#31774](https://github.com/airbytehq/airbyte/pull/31774)  | Add a docker configuration check on `airbyte-ci` startup.                                                                  |
| 2.5.0   | [#31766](https://github.com/airbytehq/airbyte/pull/31766)  | Support local connectors secrets.                                                                                          |
| 2.4.0   | [#31716](https://github.com/airbytehq/airbyte/pull/31716)  | Enable pre-release publish with local CDK.                                                                                 |
| 2.3.1   | [#31748](https://github.com/airbytehq/airbyte/pull/31748)  | Use AsyncClick library instead of base Click.                                                                              |
| 2.3.0   | [#31699](https://github.com/airbytehq/airbyte/pull/31699)  | Support optional concurrent CAT execution.                                                                                 |
| 2.2.6   | [#31752](https://github.com/airbytehq/airbyte/pull/31752)  | Only authenticate when secrets are available.                                                                              |
| 2.2.5   | [#31718](https://github.com/airbytehq/airbyte/pull/31718)  | Authenticate the sidecar docker daemon to DockerHub.                                                                       |
| 2.2.4   | [#31535](https://github.com/airbytehq/airbyte/pull/31535)  | Improve gradle caching when building java connectors.                                                                      |
| 2.2.3   | [#31688](https://github.com/airbytehq/airbyte/pull/31688)  | Fix failing `CheckBaseImageUse` step when not running on PR.                                                               |
| 2.2.2   | [#31659](https://github.com/airbytehq/airbyte/pull/31659)  | Support builds on x86_64 platform                                                                                          |
| 2.2.1   | [#31653](https://github.com/airbytehq/airbyte/pull/31653)  | Fix CheckBaseImageIsUsed failing on non certified connectors.                                                              |
| 2.2.0   | [#30527](https://github.com/airbytehq/airbyte/pull/30527)  | Add a new check for python connectors to make sure certified connectors use our base image.                                |
| 2.1.1   | [#31488](https://github.com/airbytehq/airbyte/pull/31488)  | Improve `airbyte-ci` start time with Click Lazy load                                                                       |
| 2.1.0   | [#31412](https://github.com/airbytehq/airbyte/pull/31412)  | Run airbyte-ci from any where in airbyte project                                                                           |
| 2.0.4   | [#31487](https://github.com/airbytehq/airbyte/pull/31487)  | Allow for third party connector selections                                                                                 |
| 2.0.3   | [#31525](https://github.com/airbytehq/airbyte/pull/31525)  | Refactor folder structure                                                                                                  |
| 2.0.2   | [#31533](https://github.com/airbytehq/airbyte/pull/31533)  | Pip cache volume by python version.                                                                                        |
| 2.0.1   | [#31545](https://github.com/airbytehq/airbyte/pull/31545)  | Reword the changelog entry when using `migrate_to_base_image`.                                                             |
| 2.0.0   | [#31424](https://github.com/airbytehq/airbyte/pull/31424)  | Remove `airbyte-ci connectors format` command.                                                                             |
| 1.9.4   | [#31478](https://github.com/airbytehq/airbyte/pull/31478)  | Fix running tests for connector-ops package.                                                                               |
| 1.9.3   | [#31457](https://github.com/airbytehq/airbyte/pull/31457)  | Improve the connector documentation for connectors migrated to our base image.                                             |
| 1.9.2   | [#31426](https://github.com/airbytehq/airbyte/pull/31426)  | Concurrent execution of java connectors tests.                                                                             |
| 1.9.1   | [#31455](https://github.com/airbytehq/airbyte/pull/31455)  | Fix `None` docker credentials on publish.                                                                                  |
| 1.9.0   | [#30520](https://github.com/airbytehq/airbyte/pull/30520)  | New commands: `bump_version`, `upgrade_base_image`, `migrate_to_base_image`.                                               |
| 1.8.0   | [#30520](https://github.com/airbytehq/airbyte/pull/30520)  | New commands: `bump_version`, `upgrade_base_image`, `migrate_to_base_image`.                                               |
| 1.7.2   | [#31343](https://github.com/airbytehq/airbyte/pull/31343)  | Bind Pytest integration tests to a dockerhost.                                                                             |
| 1.7.1   | [#31332](https://github.com/airbytehq/airbyte/pull/31332)  | Disable Gradle step caching on source-postgres.                                                                            |
| 1.7.0   | [#30526](https://github.com/airbytehq/airbyte/pull/30526)  | Implement pre/post install hooks support.                                                                                  |
| 1.6.0   | [#30474](https://github.com/airbytehq/airbyte/pull/30474)  | Test connector inside their containers.                                                                                    |
| 1.5.1   | [#31227](https://github.com/airbytehq/airbyte/pull/31227)  | Use python 3.11 in amazoncorretto-bazed gradle containers, run 'test' gradle task instead of 'check'.                      |
| 1.5.0   | [#30456](https://github.com/airbytehq/airbyte/pull/30456)  | Start building Python connectors using our base images.                                                                    |
| 1.4.6   | [ #31087](https://github.com/airbytehq/airbyte/pull/31087) | Throw error if airbyte-ci tools is out of date                                                                             |
| 1.4.5   | [#31133](https://github.com/airbytehq/airbyte/pull/31133)  | Fix bug when building containers using `with_integration_base_java_and_normalization`.                                     |
| 1.4.4   | [#30743](https://github.com/airbytehq/airbyte/pull/30743)  | Add `--disable-report-auto-open` and `--use-host-gradle-dist-tar` to allow gradle integration.                             |
| 1.4.3   | [#30595](https://github.com/airbytehq/airbyte/pull/30595)  | Add --version and version check                                                                                            |
| 1.4.2   | [#30595](https://github.com/airbytehq/airbyte/pull/30595)  | Remove directory name requirement                                                                                          |
| 1.4.1   | [#30595](https://github.com/airbytehq/airbyte/pull/30595)  | Load base migration guide into QA Test container for strict encrypt variants                                               |
| 1.4.0   | [#30330](https://github.com/airbytehq/airbyte/pull/30330)  | Add support for pyproject.toml as the prefered entry point for a connector package                                         |
| 1.3.0   | [#30461](https://github.com/airbytehq/airbyte/pull/30461)  | Add `--use-local-cdk` flag to all connectors commands                                                                      |
| 1.2.3   | [#30477](https://github.com/airbytehq/airbyte/pull/30477)  | Fix a test regression introduced the previous version.                                                                     |
| 1.2.2   | [#30438](https://github.com/airbytehq/airbyte/pull/30438)  | Add workaround to always stream logs properly with --is-local.                                                             |
| 1.2.1   | [#30384](https://github.com/airbytehq/airbyte/pull/30384)  | Java connector test performance fixes.                                                                                     |
| 1.2.0   | [#30330](https://github.com/airbytehq/airbyte/pull/30330)  | Add `--metadata-query` option to connectors command                                                                        |
| 1.1.3   | [#30314](https://github.com/airbytehq/airbyte/pull/30314)  | Stop patching gradle files to make them work with airbyte-ci.                                                              |
| 1.1.2   | [#30279](https://github.com/airbytehq/airbyte/pull/30279)  | Fix correctness issues in layer caching by making atomic execution groupings                                               |
| 1.1.1   | [#30252](https://github.com/airbytehq/airbyte/pull/30252)  | Fix redundancies and broken logic in GradleTask, to speed up the CI runs.                                                  |
| 1.1.0   | [#29509](https://github.com/airbytehq/airbyte/pull/29509)  | Refactor the airbyte-ci test command to run tests on any poetry package.                                                   |
| 1.0.0   | [#28000](https://github.com/airbytehq/airbyte/pull/29232)  | Remove release stages in favor of support level from airbyte-ci.                                                           |
| 0.5.0   | [#28000](https://github.com/airbytehq/airbyte/pull/28000)  | Run connector acceptance tests with dagger-in-dagger.                                                                      |
| 0.4.7   | [#29156](https://github.com/airbytehq/airbyte/pull/29156)  | Improve how we check existence of requirement.txt or setup.py file to not raise early pip install errors.                  |
| 0.4.6   | [#28729](https://github.com/airbytehq/airbyte/pull/28729)  | Use keyword args instead of positional argument for optional paramater in Dagger's API                                     |
| 0.4.5   | [#29034](https://github.com/airbytehq/airbyte/pull/29034)  | Disable Dagger terminal UI when running publish.                                                                           |
| 0.4.4   | [#29064](https://github.com/airbytehq/airbyte/pull/29064)  | Make connector modified files a frozen set.                                                                                |
| 0.4.3   | [#29033](https://github.com/airbytehq/airbyte/pull/29033)  | Disable dependency scanning for Java connectors.                                                                           |
| 0.4.2   | [#29030](https://github.com/airbytehq/airbyte/pull/29030)  | Make report path always have the same prefix: `airbyte-ci/`.                                                               |
| 0.4.1   | [#28855](https://github.com/airbytehq/airbyte/pull/28855)  | Improve the selected connectors detection for connectors commands.                                                         |
| 0.4.0   | [#28947](https://github.com/airbytehq/airbyte/pull/28947)  | Show Dagger Cloud run URLs in CI                                                                                           |
| 0.3.2   | [#28789](https://github.com/airbytehq/airbyte/pull/28789)  | Do not consider empty reports as successfull.                                                                              |
| 0.3.1   | [#28938](https://github.com/airbytehq/airbyte/pull/28938)  | Handle 5 status code on MetadataUpload as skipped                                                                          |
| 0.3.0   | [#28869](https://github.com/airbytehq/airbyte/pull/28869)  | Enable the Dagger terminal UI on local `airbyte-ci` execution                                                              |
| 0.2.3   | [#28907](https://github.com/airbytehq/airbyte/pull/28907)  | Make dagger-in-dagger work for `airbyte-ci tests` command                                                                  |
| 0.2.2   | [#28897](https://github.com/airbytehq/airbyte/pull/28897)  | Sentry: Ignore error logs without exceptions from reporting                                                                |
| 0.2.1   | [#28767](https://github.com/airbytehq/airbyte/pull/28767)  | Improve pytest step result evaluation to prevent false negative/positive.                                                  |
| 0.2.0   | [#28857](https://github.com/airbytehq/airbyte/pull/28857)  | Add the `airbyte-ci tests` command to run the test suite on any `airbyte-ci` poetry package.                               |
| 0.1.1   | [#28858](https://github.com/airbytehq/airbyte/pull/28858)  | Increase the max duration of Connector Package install to 20mn.                                                            |
| 0.1.0   |                                                            | Alpha version not in production yet. All the commands described in this doc are available.                                 |

## More info

This project is owned by the Connectors Operations team. We share project updates and remaining
stories before its release to production in this
[EPIC](https://github.com/airbytehq/airbyte/issues/24403).

# Troubleshooting

## Commands

### `make tools.airbyte-ci.check`

This command checks if the `airbyte-ci` command is appropriately installed.

### `make tools.airbyte-ci.clean`

This command removes the `airbyte-ci` command from your system.

## Common issues

### `airbyte-ci` is not found

If you get the following error when running `airbyte-ci`:

```bash
$ airbyte-ci
zsh: command not found: airbyte-ci
```

It means that the `airbyte-ci` command is not in your PATH.

Try running

```bash
make make tools.airbyte-ci.check
```

For some hints on how to fix this.

But when in doubt it can be best to run

```bash
make tools.airbyte-ci.clean
```

Then reinstall the CLI with

```bash
make tools.airbyte-ci.install
```

## Development

### `airbyte-ci` is not found

To fix this, you can either:

- Ensure that airbyte-ci is installed with pipx. Run `pipx list` to check if airbyte-ci is
  installed.
- Run `pipx ensurepath` to add the pipx binary directory to your PATH.
- Add the pipx binary directory to your PATH manually. The pipx binary directory is usually
  `~/.local/bin`.

### python3.10 not found

If you get the following error when running
`pipx install --editable --force --python=python3.10 airbyte-ci/connectors/pipelines/`:

```bash
$ pipx install --editable --force --python=python3.10 airbyte-ci/connectors/pipelines/
Error: Python 3.10 not found on your system.
```

It means that you don't have Python 3.10 installed on your system.

To fix this, you can either:

- Install Python 3.10 with pyenv. Run `pyenv install 3.10` to install the latest Python version.
- Install Python 3.10 with your system package manager. For instance, on Ubuntu you can run
  `sudo apt install python3.10`.
- Ensure that Python 3.10 is in your PATH. Run `which python3.10` to check if Python 3.10 is
  installed and in your PATH.

### Any type of pipeline failure

First you should check that the version of the CLI you are using is the latest one. You can check
the version of the CLI with the `--version` option:

```bash
$ airbyte-ci --version
airbyte-ci, version 0.1.0
```

and compare it with the version in the pyproject.toml file:

```bash
$ cat airbyte-ci/connectors/pipelines/pyproject.toml | grep version
```

If you get any type of pipeline failure, you can run the pipeline with the `--show-dagger-logs`
option to get more information about the failure.

```bash
$ airbyte-ci --show-dagger-logs connectors --name=source-pokeapi test
```

and when in doubt, you can reinstall the CLI with the `--force` option:

```bash
$ pipx reinstall pipelines --force
```
