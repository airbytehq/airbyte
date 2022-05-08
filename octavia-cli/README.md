# 🐙 Octavia CLI

## Disclaimer

The project is in **alpha** version.
Readers can refer to our [opened GitHub issues](https://github.com/airbytehq/airbyte/issues?q=is%3Aopen+is%3Aissue+label%3Aarea%2Foctavia-cli) to check the ongoing work on this project.


## What is `octavia` CLI?

Octavia CLI is a tool to manage Airbyte configurations in YAML.
It has the following features:

- Scaffolding of a readable directory architecture that will host the YAML configs (`octavia init`).
- Auto-generation of YAML config file that matches the resources' schemas (`octavia generate`).
- Manage Airbyte resources with YAML config files.
- Safe resources update through diff display and validation (`octavia apply`).
- Simple secret management to avoid versioning credentials.

## Why should I use `octavia` CLI?

A CLI provides freedom to users to use the tool in whatever context and use case they have.
These are non-exhaustive use cases `octavia` can be convenient for:

- Managing Airbyte configurations with a CLI instead of a web UI.
- Versioning Airbyte configurations in Git.
- Updating of Airbyte configurations in an automated deployment pipeline.
- Integrating the Airbyte configuration deployment in a dev ops tooling stack: Helm, Ansible etc.
- Streamlining the deployment of Airbyte configurations to multiple Airbyte instance.

Feel free to share your use cases with the community in [#octavia-cli](https://airbytehq.slack.com/archives/C02RRUG9CP5) or on [Discourse](https://discuss.airbyte.io/).

## Table of content

- [Workflow](#workflow)
- [Secret management](#secret-management)
- [Install](#install)
- [Commands reference](#commands-reference)
- [Contributing](#contributing)
- [Telemetry](#telemetry)
- [Changelog](#changelog)

## Workflow

### 1. Generate local YAML files for sources or destinations

1. Retrieve the *definition id* of the connector you want to use using `octavia list command`.
2. Generate YAML configuration running `octavia generate source <DEFINITION_ID> <SOURCE_NAME>` or `octavia generate destination <DEFINITION_ID> <DESTINATION_NAME>`.

### 2. Edit your local YAML configurations

1. Edit the generated YAML configurations according to your need.
2. Use the [secret management feature](#secret-management) feature to avoid storing credentials in the YAML files.

### 3. Create the declared sources or destinations on your Airbyte instance

1. Run `octavia apply` to create the **sources** and **destinations**

### 4. Generate connections

1. Run `octavia octavia generate connection --source <PATH_TO_SOURCE_CONFIG> --destination <PATH_TO_DESTINATION_CONFIG> <CONNECTION_NAME>` to create a YAML configuration for a new connection.
2. Edit the created configuration file according to your need: change the scheduling or the replicated streams list.

### 5. Create the declared connections

1. Run `octavia apply` to create the newly declared connection on your Airbyte instance.

### 6. Update your configurations

Changes in your local configurations can be propagated to your Airbyte instance using `octavia apply`.  You will be prompted for validation of changes. You can bypass the validation step using the `--force` flag.

## Secret management

Sources and destinations configurations have credential fields that you **do not want to store as plain text in your VCS**.
`octavia` offers secret management through environment variables expansion:

```yaml
configuration:
  password: ${MY_PASSWORD}
```

If you have set a  `MY_PASSWORD` environment variable, `octavia apply` will load its value into the `password` field.

## Install

### Requirements

We decided to package the CLI in a docker image with portability in mind.
**[Please install and run Docker if you are not](https://docs.docker.com/get-docker/)**.

### As a command available in your bash profile

```bash
curl -s -o- https://raw.githubusercontent.com/airbytehq/airbyte/master/octavia-cli/install.sh | bash
```

This script:

1. Pulls the [octavia-cli image](https://hub.docker.com/r/airbyte/octavia-cli/tags) from our Docker registry.
2. Creates an `octavia` alias in your profile.
3. Creates a `~/.octavia` file whose values are mapped to the octavia container's environment variables.

### Using `docker run`

```bash
touch ~/.octavia # Create a file to store env variables that will be mapped the octavia-cli container
mkdir my_octavia_project_directory # Create your octavia project directory where YAML configurations will be stored.
docker run --name octavia-cli -i --rm -v my_octavia_project_directory:/home/octavia-project --network host --user $(id -u):$(id -g) --env-file ~/.octavia airbyte/octavia-cli:0.37.0-alpha
```

### Using `docker-compose`

Using octavia in docker-compose could be convenient for automatic `apply` on start-up.

Add another entry in the services key of your Airbyte `docker-compose.yml`

```yaml
services:
  # . . .
  octavia-cli:
    image: airbyte/octavia-cli:latest
    command: apply --force
    env_file:
      - ~/.octavia # Use a local env file to store variables that will be mapped the octavia-cli container
    volumes:
      - <path_to_your_local_octavia_project_directory>:/home/octavia-project
    depends_on:
      - webapp
```

Other commands besides `apply` can be run like so:

```bash
docker-compose run octavia-cli <command>`
```

## Commands reference

### `octavia` command flags

| **Flag**                                 | **Description**                                  | **Env Variable**           | **Default**                                            |
|------------------------------------------|--------------------------------------------------|----------------------------|--------------------------------------------------------|
| `--airbyte-url`                          | Airbyte instance URL.                            | `AIRBYTE_URL`              | `http://localhost:8000`                                |
| `--workspace-id`                         | Airbyte workspace id.                            | `AIRBYTE_WORKSPACE_ID`     | The first workspace id found on your Airbyte instance. |
| `--enable-telemetry/--disable-telemetry` | Enable or disable the sending of telemetry data. | `OCTAVIA_ENABLE_TELEMETRY` | True                                                   |

### `octavia` subcommands

| **Command**                             | **Usage**                                                                           |
|-----------------------------------------|-------------------------------------------------------------------------------------|
| **`octavia init`**                        | Initialize required directories for the project.                                  |
| **`octavia list connectors sources`**     | List all sources connectors available on the remote Airbyte instance.             |
| **`octavia list connectors destination`** | List all destinations connectors available on the remote Airbyte instance.        |
| **`octavia list workspace sources`**      | List existing sources in current the Airbyte workspace.                           |
| **`octavia list workspace destinations`** | List existing destinations in the current Airbyte workspace.                      |
| **`octavia list workspace connections`**  | List existing connections in the current Airbyte workspace.                       |
| **`octavia generate source`**             | Generate a local YAML configuration for a new source.                             |
| **`octavia generate destination`**        | Generate a local YAML configuration for a new destination.                        |
| **`octavia generate connection`**         | Generate a local YAML configuration for a new connection.                         |
| **`octavia apply`**                       | Create or update Airbyte remote resources according to local YAML configurations. |

#### `octavia init`

The `octavia init` commands scaffolds the required directory architecture for running `octavia generate` and `octavia apply` commands.

**Example**:

```bash
$ mkdir my_octavia_project && cd my_octavia_project
$ octavia init
🐙 - Octavia is targetting your Airbyte instance running at http://localhost:8000 on workspace e1f46f7d-5354-4200-aed6-7816015ca54b.
🐙 - Project is not yet initialized.
🔨 - Initializing the project.
✅ - Created the following directories: sources, destinations, connections.
$ ls
connections  destinations sources
```

#### `octavia list connectors sources`

List all the source connectors currently available on your Airbyte instance.

**Example**:

```bash
$ octavia list connectors sources
NAME                            DOCKER REPOSITORY                              DOCKER IMAGE TAG  SOURCE DEFINITION ID
Airtable                        airbyte/source-airtable                        0.1.1             14c6e7ea-97ed-4f5e-a7b5-25e9a80b8212
AWS CloudTrail                  airbyte/source-aws-cloudtrail                  0.1.4             6ff047c0-f5d5-4ce5-8c81-204a830fa7e1
Amazon Ads                      airbyte/source-amazon-ads                      0.1.3             c6b0a29e-1da9-4512-9002-7bfd0cba2246
Amazon Seller Partner           airbyte/source-amazon-seller-partner           0.2.16            e55879a8-0ef8-4557-abcf-ab34c53ec460
```

#### `octavia list connectors destinations`

List all the destinations connectors currently available on your Airbyte instance.

**Example**:

```bash
$ octavia list connectors destinations
NAME                                  DOCKER REPOSITORY                                 DOCKER IMAGE TAG  DESTINATION DEFINITION ID
Azure Blob Storage                    airbyte/destination-azure-blob-storage            0.1.3             b4c5d105-31fd-4817-96b6-cb923bfc04cb
Amazon SQS                            airbyte/destination-amazon-sqs                    0.1.0             0eeee7fb-518f-4045-bacc-9619e31c43ea
BigQuery                              airbyte/destination-bigquery                      0.6.11            22f6c74f-5699-40ff-833c-4a879ea40133
BigQuery (denormalized typed struct)  airbyte/destination-bigquery-denormalized         0.2.10            079d5540-f236-4294-ba7c-ade8fd918496
```

#### `octavia list workspace sources`

List all the sources existing on your targeted Airbyte instance.

**Example**:

```bash
$ octavia list workspace sources
NAME     SOURCE NAME  SOURCE ID
weather  OpenWeather  c4aa8550-2122-4a33-9a21-adbfaa638544
```

#### `octavia list workspace destinations`

List all the destinations existing on your targeted Airbyte instance.

**Example**:

```bash
$ octavia list workspace destinations
NAME   DESTINATION NAME  DESTINATION ID
my_db  Postgres          c0c977c2-48e7-46fe-9f57-576285c26d42
```

#### `octavia list workspace connections`

List all the connections existing on your targeted Airbyte instance.

**Example**:

```bash
$ octavia list workspace connections
NAME           CONNECTION ID                         STATUS  SOURCE ID                             DESTINATION ID
weather_to_pg  a4491317-153e-436f-b646-0b39338f9aab  active  c4aa8550-2122-4a33-9a21-adbfaa638544  c0c977c2-48e7-46fe-9f57-576285c26d42
```

#### `octavia generate source <DEFINITION_ID> <SOURCE_NAME>`

Generate a YAML configuration for a source.
The YAML file will be stored at `./sources/<resource_name>/configuration.yaml`.

| **Argument**    | **Description**                                                                              |
|-----------------|-----------------------------------------------------------------------------------------------|
| `DEFINITION_ID` | The source connector definition id. Can be retrieved using `octavia list connectors sources`. |
| `SOURCE_NAME`   | The name you want to give to this source in Airbyte.                                          |

**Example**:

```bash
$ octavia generate source d8540a80-6120-485d-b7d6-272bca477d9b weather
✅ - Created the source template for weather in ./sources/weather/configuration.yaml.
```

#### `octavia generate destination <DEFINITION_ID> <DESTINATION_NAME>`

Generate a YAML configuration for a destination.
The YAML file will be stored at `./destinations/<destination_name>/configuration.yaml`.

| **Argument**       | **Description**                                                                                         |
|--------------------|---------------------------------------------------------------------------------------------------------|
| `DEFINITION_ID`    | The destination connector definition id. Can be retrieved using `octavia list connectors destinations`. |
| `DESTINATION_NAME` | The name you want to give to this destination in Airbyte.                                               |

**Example**:

```bash
$ octavia generate destination 25c5221d-dce2-4163-ade9-739ef790f503 my_db
✅ - Created the destination template for my_db in ./destinations/my_db/configuration.yaml.
```

#### `octavia generate connection --source <path-to-source-configuration.yaml> --destination <path-to-destination-configuration.yaml> <CONNECTION_NAME>`

Generate a YAML configuration for a connection.
The YAML file will be stored at `./connections/<connection_name>/configuration.yaml`.

| **Option**      | **Required** | **Description**                                                                            |
|-----------------|--------------|--------------------------------------------------------------------------------------------|
| `--source`      | Yes          | Path to the YAML configuration file of the source you want to create a connection from.    |
| `--destination` | Yes          | Path to the YAML configuration file of the destination you want to create a connection to. |

| **Argument**      | **Description**                                          |
|-------------------|----------------------------------------------------------|
| `CONNECTION_NAME` | The name you want to give to this connection in Airbyte. |

**Example**:

```bash
$ octavia generate connection --source sources/weather/configuration.yaml --destination destinations/my_db/configuration.yaml weather_to_pg
✅ - Created the connection template for weather_to_pg in ./connections/weather_to_pg/configuration.yaml.
```

#### `octavia apply`

Create or update the resource on your Airbyte instance according to local configurations found in your octavia project directory.
If the resource was not found on your Airbyte instance, **apply** will **create** the remote resource.
If the resource was found on your Airbyte instance, **apply** will prompt you for validation of the changes and will run an **update** of your resource.
Please note that if a secret field was updated on your configuration, **apply** will run this change without prompt.

| **Option**      | **Required** | **Description**                                                                            |
|-----------------|--------------|--------------------------------------------------------------------------------------------|
| `--file`        | No           | Path to the YAML configuration files you want to create or update.                         |
| `--force`       | No           | Run update without prompting for changes validation.                                       |

**Example**:

```bash
$ octavia apply
🐙 - weather exists on your Airbyte instance, let's check if we need to update it!
👀 - Here's the computed diff (🚨 remind that diff on secret fields are not displayed):
  E - Value of root['lat'] changed from "46.7603" to "45.7603".
❓ - Do you want to update weather? [y/N]: y
✍️ - Running update because a diff was detected between local and remote resource.
🎉 - Successfully updated weather on your Airbyte instance!
💾 - New state for weather stored at ./sources/weather/state.yaml.
🐙 - my_db exists on your Airbyte instance, let's check if we need to update it!
😴 - Did not update because no change detected.
🐙 - weather_to_pg exists on your Airbyte instance, let's check if we need to update it!
👀 - Here's the computed diff (🚨 remind that diff on secret fields are not displayed):
  E - Value of root['schedule']['timeUnit'] changed from "days" to "hours".
❓ - Do you want to update weather_to_pg? [y/N]: y
✍️ - Running update because a diff was detected between local and remote resource.
🎉 - Successfully updated weather_to_pg on your Airbyte instance!
💾 - New state for weather_to_pg stored at ./connections/weather_to_pg/state.yaml.
```

## Contributing

1. Please sign up to [Airbyte's Slack workspace](https://slack.airbyte.io/) and join the `#octavia-cli`. We'll sync up community efforts in this channel.
2. Pick an existing [GitHub issues](https://github.com/airbytehq/airbyte/issues?q=is%3Aopen+is%3Aissue+label%3Aarea%2Foctavia-cli) or **open** a new one to explain what you'd like to implement.
3. Assign the GitHub issue to yourself.
4. Fork Airbyte's repo, code and test thoroughly.
5. Open a PR on our Airbyte repo from your fork.

### Developing locally

0. Build the project locally (from the root of Airbyte's repo): `SUB_BUILD=OCTAVIA_CLI ./gradlew build # from the root directory of the repo`.
1. Install Python 3.8.12. We suggest doing it through `pyenv`.
2. Create a virtualenv: `python -m venv .venv`.
3. Activate the virtualenv: `source .venv/bin/activate`.
4. Install dev dependencies: `pip install -e .\[tests\]`.
5. Install `pre-commit` hooks: `pre-commit install`.
6. Run the unittest suite: `pytest --cov=octavia_cli`.
7. Make sure the build passes (step 0) before opening a PR.

## Telemetry
This CLI has some telemetry tooling to send Airbyte some data about the usage of this tool.
We will use this data to improve the CLI and measure its adoption.
The telemetry sends data about:
* Which command was run (not the arguments or options used).
* Success or failure of the command run and the error type (not the error payload).
* The current Airbyte workspace id if the user has not set the *anonymous data collection* on their Airbyte instance.

You can disable telemetry by setting the `OCTAVIA_ENABLE_TELEMETRY` environment variable to `False` or using the `--disable-telemetry` flag.

## Changelog

| Version | Date       | Description                         | PR                                                       |
|---------|------------|-------------------------------------|----------------------------------------------------------|
| 0.36.11 | 2022-05-05 | Use snake case in connection fields | [#12133](https://github.com/airbytehq/airbyte/pull/12133)|
| 0.36.2  | 2022-04-15 | Improve telemetry                   | [#12072](https://github.com/airbytehq/airbyte/issues/11896)|
| 0.35.68 | 2022-04-12 | Add telemetry                       | [#11896](https://github.com/airbytehq/airbyte/issues/11896)|
| 0.35.61 | 2022-04-07 | Alpha release                       | [EPIC](https://github.com/airbytehq/airbyte/issues/10704)|
