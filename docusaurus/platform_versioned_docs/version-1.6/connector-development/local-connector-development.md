# Developing Connectors Locally

This document outlines the tools needed to develop connectors locally, and how to use each tool.

:::tip
**Using Connector Builder**

For most cases, when building new source connectors, we recommend starting with our [**Low-Code Connector Builder**](./connector-builder-ui/overview) instead of starting from the development tools described here. The Connector Builder provides the most streamlined experience for building new connectors, with little or no code, and directly within the Airbyte web interface.
:::

## Tooling

When developing connectors locally, you'll want to ensure the following tools are installed:

1. [**Poe the Poet**](#poe-the-poet) - Used as a common task interface for defining and running development tasks.
1. [`uv`](#uv) - Used for installing Python-based CLI apps, such as `Poe`.
1. [`docker`](#docker) - Used when building and running connector container images.
1. [`gradle`](#gradle) - Required when working with Java and Kotlin connectors.
1. [Airbyte CDKs](#airbyte-connector-development-kits-cdks) - The Airbyte Connector Development Kit (CDK) tools, including the [`airbyte-cdk` CLI](#the-airbyte-cdk-cli).
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

### Airbyte Connector Development Kits (CDKs)

What we loosely refer to as the "Airbyte CDK" is actually a combination of several CDKs and tools:

1. [**Python CDK**](https://airbytehq.github.io/airbyte-python-cdk/airbyte_cdk.html) - A developer kit that includes the foundation for low-code and no-code connectors, as well as several other Python-based implementations.
1. **File CDK** - A CDK for building file-based source connectors, built on the Python CDK.
1. **Airbyte CDK CLI** - A command line interface (CLI) for performing common connector-related tasks, built into the Python CDK. (See [below](#the-airbyte-cdk-cli) for installation instructions.)

For high-throughput connectors, we also use:

1. **Bulk Load CDK** - A set of libraries and resources for building destinations using the Kotlin language.
1. **Bulk Extract CDK** - A set of libraries and resources for building sources using the Kotlin language.

#### The `airbyte-cdk` CLI

To install the `airbyte-cdk` CLI, first install `uv` using the instructions above. Then you can install or upgrade the `airbyte-cdk` CLI using:

```bash
uv install --upgrade 'airbyte-cdk[dev]'
```

For a list of available commands in the `airbyte-cdk` CLI, run `airbyte-cdk --help`.

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

## Managing Connector Secrets in GSM

Airbyte tools and CI workflows will expect secrets to be stored in Google Secrets Manager (GCP) using the following conventions:

1. Each secret value stored in GSM must be a fully formed JSON config object.
   - For the purpose of this section, the term "connector secret" is interchangeable with "connector config" containing one or more sensitive values.
2. Each connector secret value stored in GSM should have two labels:
   1. `connector: <connector-name>`: indicates the name of the connector that the secret pertains to.
      - For example, `connector: source-s3` will be used when testing the S3 source connector.
   2. `filename: <use-case-name>`: The use case name or scenario name that is being declared.
      - Common `filename` values are: `config` (default), `invalid_config`, `oauth_config`, etc.
      - When fetching secrets locally, the label `filename: oauth_config` value will result in a config file being fetched with the name `secrets/oauth_config.json`.
      - Note: Google Secrets Manager does not support including the "`.`" character in label text, which is why the label should always be stored without the `.json` suffix.
3. Airbyte tooling will authenticate to your GSM instance using the following two env vars:
   1. `GCP_PROJECT_ID` - This is your alphanumeric project name, which tells Airbyte which project ID to authenticate against when fetching secrets.
      - Airbyte CI workflows will look for this value as a [**repo-level variable**](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/store-information-in-variables#creating-configuration-variables-for-a-repository) with the same name.
   1. `GCP_GSM_CREDENTIALS` - A variable containing the GCP credentials JSON text for your service account.
      - Airbyte CI workflows will look for this value as a [**repo-level secret**](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions) with the same name.

### Understanding the required secrets for testing

To understand which secrets are required for a connector, consult the `metadata.yaml` and `acceptance-test-config.yml` files within the connector directory.

### Fetching and Listing Connector Secrets Locally

To view a list of secrets, or to fetch them locally, you can use the [Airbyte CDK CLI](#the-airbyte-cdk-cli):

- `airbyte-cdk secrets --help` - Gives general usage instructions for the `secrets` CLI functions.
- `airbyte-cdk secrets list` - Lists the secrets available for the given connector, along with a GSM deep link to each available secret.
  - Note: The `secrets list` command is purely a metadata operation; no secrets are downloaded to your machine locally when running this step.
- `airbyte-cdk secrets fetch`
  - Fetching the secrets saves them to local `.json` files within in the connector's `secrets`, making them available for local connector testing.

:::caution
The `secrets` directory should be automatically excluded from git based upon repo-level `.gitignore` rules. It is always a good idea to confirm that this is true for your case, and please always use caution whenever handling sensitive credentials.
:::

## PR Slash Commands

Maintainers can execute any of the following connector admin commands upon request:

- `/bump-version` - Run the bump version command, which advances the connector version(s) and adds a changelog entry for any modified connector(s).
- `/format-fix` - Fixes any formatting issues.
- `/run-connector-tests` - Run the connector tests for any modified connectors.
- `/run-cat-tests` - Run the legacy connector acceptance tests (CAT) for any modified connectors. This is helpful if the connector has poor test coverage overall.
- `/build-connector-images` - Builds and publishes a pre-release docker image for the modified connector(s).
- `/poe` - Run a Poe task.

When working on PRs from forks, maintainers can apply `/format-fix` to help expedite formatting fixes, and `/run-connector-tests` if the fork does not have sufficient secrets bootstrapping or other permissions needed to fully test the connector changes.

Note:

- Slash commands may only be executed by maintainers, and they run with the context and the permissions from the main repo.
