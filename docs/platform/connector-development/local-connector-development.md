# Developing Connectors Locally

This document outlines the tools needed to develop connectors locally, and how to use each tool.

## Tooling

When developing connectors locally, you'll want to ensure the following tools are installed:

1. [**Poe the Poet**](#poe-the-poet) - Used as a common task interface for defining and running development tasks.
1. [`uv`](#uv) - Used for installing Python-based CLI apps, such as `Poe`.
1. [`docker`](#docker) - Used when building and running connector container images.
1. [`gradle`](#gradle) - Required when working with Java and Kotlin connectors.
1. [`airbyte-ci` (deprecated)](#airbyte-ci-deprecated) - Used for a large number of tasks such as building and publishing.

### Poe the Poet

[Poe the Poet](https://poethepoet.natn.io) - This tool allows you to perform common connector tasks from a single entrypoint.

You can install using `brew` (recommended) or with [another package manager](https://poethepoet.natn.io/installation.html#):

```bash
brew tap nat-n/poethepoet
brew install nat-n/poethepoet/poethepoet
```

To see a list of available tasks, run `poe` from any directory in the `airbyte` repo.

Notes:

1. When running `poe` from the root of the repo, you'll have the options `connector`, `source`, and `destination`. These will each pass the tasks you request along to the specified connector's directory.
2. When running `poe` from a connector directory, you'll get a specific list of available tasks, like `lint`, `check-all`, etc. The available commands may vary by connector and connector type (java vs python vs manifest-only), so run `poe` on its own to see what commands are available.
3. Poe tasks are there to help you, but they are _not_ the only way to run a task. Please feel encouraged to review, copy, paste, or combing steps from the task definitions in the `poe_tasks` directory. And if you find task invocation patterns that are especially helpful, please consider contributing back to those task definition files by creating a new PR.

:::tip

You can find the global Poe task definitions for any connector in the `poe_tasks` directory at the root of the Airbyte repo. These definitions can be a helpful reference if you want to decompose or combine certain tasks to suite your preference or to plug these commands natively into your IDE of choice.

:::

### UV

UV is a tool for installing and managing Python applications. It replaces `pip`, `pipx`, and a number of other tools. It is also the recommended way to install Python CLI apps like `poe`.

To install or upgrade `uv`:

```bash
brew install uv
```

### Docker

We recommend using Docker Desktop or Orbstack, although other container runtimes might work as well. A full discussion of how to install and use docker is outside the scope of this guide.

See [Debugging Docker](./debugging-docker.md) for common tips and tricks.

### Gradle

Gradle is used in Java and Kotlin development. A full discussion of how to install and use docker is outside the scope of this guide. Similar to running `poe`, you can run `gradle tasks` to view a list of available Gradle development tasks.

:::tip

You can also use `poe` to execute Gradle tasks, often with less typing. From within a connector directory you can run `poe gradle tasks` for a list of Gradle tasks that apply to the connector and `poe gradle TASK_NAME` to run a given Gradle task for that connector.

Using this syntax you can avoid the long task prefixes such as typing `gradle :integration-tests:connectors:source-mysource:unitTest` and instead run `poe gradle unitTest` within the connector directory.

:::

### airbyte-ci (deprecated)

Airbyte CI `(airbyte-ci`) is a Dagger-based tool for accomplishing specific tasks. See `airbyte-ci --help` for a list of commands you can run.

:::warning
The Airbyte CI tool is now deprecated and will be phased out shortly. Most airbyte-ci commands have a simpler equivalent in Poe, which you can discover using `poe --help`.
:::

## Common Development Tasks

### Installing Connector Dependencies

If a connector has any prerequisites or dependencies to install, you can install them using `poe install`. The `install` task is a generic interface for all connectors - for instance, in Python `install` runs `poetry install --all-extras` and for Gradle, it warms the Gradle cache and builds dependencies.

### Running Tests

Regardless of connector type, you can always run connector tests using the `poe` CLI:

```bash
# Run a fast-fail set of tests:
poe test-fast

# Run all unit tests:
poe test-unit-tests

#  Run all integration tests:
poe test-integration-tests
```

:::tip

- You _do not_ have to run tests with Poe. In fact, we recommend running tests directly from your IDE whenever it makes sense to do so.
- For more information on what each step does, feel free to inspect the respective poe task files in `poe-tasks` directory at the root of the `airbyte` repo.
- For other task definitions, run `poe --help` from any connector directory.

:::

### Listing and Fetching Secrets

You can use either Poe or `airbyte-cdk` to fetch secrets. These are equivalent:

```bash
airbyte-cdk secrets fetch
poe fetch-secrets
```

Using the `airbyte-cdk` you can also list the available secrets (if any) for the given connector:

```bash
airbyte-cdk secrets list
```

The `list` command also provides you with a URL which you can use to quickly navigate to the Google Secrets Manager interface. (GCP login will be required.)

## Managing Connector Secrets

Airbyte expects secrets to be stored in Google Secrets Manager (GCP) using the following conventions:

1. Each secret should have a label called "`connector: <connector-name>`" indicating the name of the connector that the secret pertains to.
2. Each secret must be a fully formed JSON config object.
3. If more than one secret is provided, a label "`filename: <config-file-basename>`" should be set, indicating the filename with the "`.json`" suffix removed. (Google Secrets Manager does not support including the "`.`" character in label text.)
4. To understand which secrets are required for a connector, consult the `metadata.yaml` and `acceptance-test-config.yml` files within the connector directory.
5. Your fork repo should declare a secret called `GCP_GSM_CREDENTIALS` which contains the JSON text of your GCP credentials file, along with a repo variable or repo secret called `GCP_PROJECT_ID`, which contains the name of your GCP project containing your integration test credentials.
6. When testing locally, the secrets should be saved to the corresponding file names (including the `.json` suffix for each file) within the `secrets` directory inside your connector directory.
7. The `secrets` directory should be automatically excluded from git based upon the repo `.gitignore` rules, but please confirm this is true in your case, applying due caution whenever handling sensitive credentials.

Example:

If the `acceptance-test-config.yml` for `source-example` references `config.json` and `oauth_config.json`, then the following should be true:

1. Locally, we should have two files saved within the cloned repo directory, for local testing:
   1. `airbyte-integrations/connectors/source-example/secrets/config.json`
   2. `airbyte-integrations/connectors/source-example/secrets/oauth_config.json`
2. Our Google Secrets Manager (GSM) account should have the following secrets declared:
   1. `SOURCE_EXAMPLE_CONFIG_CREDS` with labels:
      - `connector: source-example`
      - `filename: config`
   2. `SOURCE_EXAMPLE_CONFIG_OAUTH_CREDS` with labels:
      - `connector: source-example`
      - `filename: oauth_config`
3. Our fork should have a repo variable or repo secret named `GCP_PROJECT_ID`, which contains the name of the GCP project that contains my integration test credentials.
4. Our fork should have a `GCP_GSM_CREDENTIALS` secret set, which contains credentials for a GCP service account with read access to the above-mentioned secrets.

## PR Slash Commands

Maintainers can execute any of the following connector admin commands upon request:

- `/bump-version` - Run the bump version command, which advances the connector version(s) and adds a changelog entry for any modified connector(s).
- `/format-fix` - Fixes any formatting issues.
- `/run-connector-tests` - Run the connector tests for any modified connectors.
- `/poe` - Run a Poe task.

When working on PRs from forks, maintainers can apply `/format-fix` to help expedite formatting fixes, and `/run-connector-tests` if the fork does not have sufficient secrets bootstrapping or other permissions needed to fully test the connector changes.

Note:

- Slash commands may only be executed by maintainers, and they run with the context and the permissions from the main repo.
