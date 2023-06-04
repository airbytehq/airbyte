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

1. Retrieve the _definition id_ of the connector you want to use using `octavia list` command.
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

Changes in your local configurations can be propagated to your Airbyte instance using `octavia apply`. You will be prompted for validation of changes. You can bypass the validation step using the `--force` flag.

## Secret management

Sources and destinations configurations have credential fields that you **do not want to store as plain text in your VCS**.
`octavia` offers secret management through environment variables expansion:

```yaml
configuration:
  password: ${MY_PASSWORD}
```

If you have set a `MY_PASSWORD` environment variable, `octavia apply` will load its value into the `password` field.

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
docker run --name octavia-cli -i --rm -v my_octavia_project_directory:/home/octavia-project --network host --user $(id -u):$(id -g) --env-file ~/.octavia airbyte/octavia-cli:0.44.11
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
docker compose run octavia-cli <command>`
```

## Commands reference

### `octavia` command flags

| **Flag**                                 | **Description**                                                                   | **Env Variable**           | **Default**                                            |
| ---------------------------------------- | --------------------------------------------------------------------------------- |----------------------------| ------------------------------------------------------ |
| `--airbyte-url`                          | Airbyte instance URL.                                                             | `AIRBYTE_URL`              | `http://localhost:8000`                                |
| `--airbyte-username`                     | Airbyte instance username (basic auth).                                           | `AIRBYTE_USERNAME`         | `airbyte`                                              |
| `--airbyte-password`                     | Airbyte instance password (basic auth).                                           | `AIRBYTE_PASSWORD`         | `password`                                             |
| `--workspace-id`                         | Airbyte workspace id.                                                             | `AIRBYTE_WORKSPACE_ID`     | The first workspace id found on your Airbyte instance. |
| `--enable-telemetry/--disable-telemetry` | Enable or disable the sending of telemetry data.                                  | `OCTAVIA_ENABLE_TELEMETRY` | True                                                   |
| `--api-http-header`                      | HTTP Header value pairs passed while calling Airbyte's API                        | None                       | None                                                   |
| `--api-http-headers-file-path`           | Path to the YAML file that contains custom HTTP Headers to send to Airbyte's API. | None                       | None                                                   |

#### Using custom HTTP headers

You can set custom HTTP headers to send to Airbyte's API with options:

```bash
octavia --api-http-header Header-Name Header-Value --api-http-header Header-Name-2 Header-Value-2 list connectors sources
```

You can also use a custom YAML file (one is already created on init in `api_http_headers.yaml`) to declare the HTTP headers to send to the API:

```yaml
headers:
  Authorization: Bearer my-secret-token
  User-Agent: octavia-cli/0.0.0
```

Environment variable expansion is available in this Yaml file

```yaml
headers:
  Authorization: Bearer ${MY_API_TOKEN}
```

**Options based headers are overriding file based headers if an header is declared in both.**

### `octavia` subcommands

| **Command**                               | **Usage**                                                                                  |
| ----------------------------------------- | ------------------------------------------------------------------------------------------ |
| **`octavia init`**                        | Initialize required directories for the project.                                           |
| **`octavia list connectors sources`**     | List all sources connectors available on the remote Airbyte instance.                      |
| **`octavia list connectors destination`** | List all destinations connectors available on the remote Airbyte instance.                 |
| **`octavia list workspace sources`**      | List existing sources in current the Airbyte workspace.                                    |
| **`octavia list workspace destinations`** | List existing destinations in the current Airbyte workspace.                               |
| **`octavia list workspace connections`**  | List existing connections in the current Airbyte workspace.                                |
| **`octavia get source`**                  | Get the JSON representation of an existing source in current the Airbyte workspace.        |
| **`octavia get destination`**             | Get the JSON representation of an existing destination in the current Airbyte workspace.   |
| **`octavia get connection`**              | Get the JSON representation of an existing connection in the current Airbyte workspace.    |
| **`octavia import all`**                  | Import all existing sources, destinations and connections to manage them with octavia-cli. |
| **`octavia import source`**               | Import an existing source to manage it with octavia-cli.                                   |
| **`octavia import destination`**          | Import an existing destination to manage it with octavia-cli.                              |
| **`octavia import connection`**           | Import an existing connection to manage it with octavia-cli.                               |
| **`octavia generate source`**             | Generate a local YAML configuration for a new source.                                      |
| **`octavia generate destination`**        | Generate a local YAML configuration for a new destination.                                 |
| **`octavia generate connection`**         | Generate a local YAML configuration for a new connection.                                  |
| **`octavia apply`**                       | Create or update Airbyte remote resources according to local YAML configurations.          |

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

#### `octavia get source <SOURCE_ID> or <SOURCE_NAME>`

Get an existing source in current the Airbyte workspace. You can use a source ID or name.

| **Argument**  | **Description**  |
| ------------- | ---------------- |
| `SOURCE_ID`   | The source id.   |
| `SOURCE_NAME` | The source name. |

**Examples**:

```bash
$ octavia get source c0c977c2-48e7-46fe-9f57-576285c26d42
{'connection_configuration': {'key': '**********',
                              'start_date': '2010-01-01T00:00:00.000Z',
                              'token': '**********'},
 'name': 'Pokemon',
 'source_definition_id': 'b08e4776-d1de-4e80-ab5c-1e51dad934a2',
 'source_id': 'c0c977c2-48e7-46fe-9f57-576285c26d42',
 'source_name': 'My Poke',
 'workspace_id': 'c4aa8550-2122-4a33-9a21-adbfaa638544'}
```

```bash
$ octavia get source "My Poke"
{'connection_configuration': {'key': '**********',
                              'start_date': '2010-01-01T00:00:00.000Z',
                              'token': '**********'},
 'name': 'Pokemon',
 'source_definition_id': 'b08e4776-d1de-4e80-ab5c-1e51dad934a2',
 'source_id': 'c0c977c2-48e7-46fe-9f57-576285c26d42',
 'source_name': 'My Poke',
 'workspace_id': 'c4aa8550-2122-4a33-9a21-adbfaa638544'}
```

#### `octavia get destination <DESTINATION_ID> or <DESTINATION_NAME>`

Get an existing destination in current the Airbyte workspace. You can use a destination ID or name.

| **Argument**       | **Description**       |
| ------------------ | --------------------- |
| `DESTINATION_ID`   | The destination id.   |
| `DESTINATION_NAME` | The destination name. |

**Examples**:

```bash
$ octavia get destination c0c977c2-48e7-46fe-9f57-576285c26d42
{
  "destinationDefinitionId": "c0c977c2-48e7-46fe-9f57-576285c26d42",
  "destinationId": "18102e7c-5160-4000-841b-15e8ec48c301",
  "workspaceId": "18102e7c-5160-4000-883a-30bc7cd65601",
  "connectionConfiguration": {
    "user": "charles"
  },
  "name": "pg",
  "destinationName": "Postgres"
}
```

```bash
$ octavia get destination pg
{
  "destinationDefinitionId": "18102e7c-5160-4000-821f-4d7cfdf87201",
  "destinationId": "18102e7c-5160-4000-841b-15e8ec48c301",
  "workspaceId": "18102e7c-5160-4000-883a-30bc7cd65601",
  "connectionConfiguration": {
    "user": "charles"
  },
  "name": "string",
  "destinationName": "string"
}
```

#### `octavia get connection <CONNECTION_ID> or <CONNECTION_NAME>`

Get an existing connection in current the Airbyte workspace. You can use a connection ID or name.

| **Argument**      | **Description**      |
| ----------------- | -------------------- |
| `CONNECTION_ID`   | The connection id.   |
| `CONNECTION_NAME` | The connection name. |

**Example**:

```bash
$ octavia get connection c0c977c2-48e7-46fe-9f57-576285c26d42
{
  "connectionId": "c0c977c2-48e7-46fe-9f57-576285c26d42",
  "name": "Poke To PG",
  "namespaceDefinition": "source",
  "namespaceFormat": "${SOURCE_NAMESPACE}",
  "prefix": "string",
  "sourceId": "18102e7c-5340-4000-8eaa-4a86f844b101",
  "destinationId": "18102e7c-5340-4000-8e58-6bed49c24b01",
  "operationIds": [
    "18102e7c-5340-4000-8ef0-f35c05a49a01"
  ],
  "syncCatalog": {
    "streams": [
      {
        "stream": {
          "name": "string",
          "jsonSchema": {},
          "supportedSyncModes": [
            "full_refresh"
          ],
          "sourceDefinedCursor": false,
          "defaultCursorField": [
            "string"
          ],
          "sourceDefinedPrimaryKey": [
            [
              "string"
            ]
          ],
          "namespace": "string"
        },
        "config": {
          "syncMode": "full_refresh",
          "cursorField": [
            "string"
          ],
          "destinationSyncMode": "append",
          "primaryKey": [
            [
              "string"
            ]
          ],
          "aliasName": "string",
          "selected": false
        }
      }
    ]
  },
  "schedule": {
    "units": 0,
    "timeUnit": "minutes"
  },
  "status": "active",
  "resourceRequirements": {
    "cpu_request": "string",
    "cpu_limit": "string",
    "memory_request": "string",
    "memory_limit": "string"
  },
  "sourceCatalogId": "18102e7c-5340-4000-85f3-204ab7715801"
}
```

```bash
$ octavia get connection "Poke To PG"
{
  "connectionId": "c0c977c2-48e7-46fe-9f57-576285c26d42",
  "name": "Poke To PG",
  "namespaceDefinition": "source",
  "namespaceFormat": "${SOURCE_NAMESPACE}",
  "prefix": "string",
  "sourceId": "18102e7c-5340-4000-8eaa-4a86f844b101",
  "destinationId": "18102e7c-5340-4000-8e58-6bed49c24b01",
  "operationIds": [
    "18102e7c-5340-4000-8ef0-f35c05a49a01"
  ],
  "syncCatalog": {
    "streams": [
      {
        "stream": {
          "name": "string",
          "jsonSchema": {},
          "supportedSyncModes": [
            "full_refresh"
          ],
          "sourceDefinedCursor": false,
          "defaultCursorField": [
            "string"
          ],
          "sourceDefinedPrimaryKey": [
            [
              "string"
            ]
          ],
          "namespace": "string"
        },
        "config": {
          "syncMode": "full_refresh",
          "cursorField": [
            "string"
          ],
          "destinationSyncMode": "append",
          "primaryKey": [
            [
              "string"
            ]
          ],
          "aliasName": "string",
          "selected": false
        }
      }
    ]
  },
  "schedule": {
    "units": 0,
    "timeUnit": "minutes"
  },
  "status": "active",
  "resourceRequirements": {
    "cpu_request": "string",
    "cpu_limit": "string",
    "memory_request": "string",
    "memory_limit": "string"
  },
  "sourceCatalogId": "18102e7c-5340-4000-85f3-204ab7715801"
}
```

#### `octavia import all`

Import all existing resources (sources, destinations, connections) on your Airbyte instance to manage them with octavia-cli.

**Examples**:

```bash
$ octavia import all
🐙 - Octavia is targetting your Airbyte instance running at http://localhost:8000 on workspace b06c6fbb-cadd-4c5c-bdbb-710add7dedb9.
✅ - Imported source poke in sources/poke/configuration.yaml. State stored in sources/poke/state_b06c6fbb-cadd-4c5c-bdbb-710add7dedb9.yaml
⚠️  - Please update any secrets stored in sources/poke/configuration.yaml
✅ - Imported destination Postgres in destinations/postgres/configuration.yaml. State stored in destinations/postgres/state_b06c6fbb-cadd-4c5c-bdbb-710add7dedb9.yaml
⚠️  - Please update any secrets stored in destinations/postgres/configuration.yaml
✅ - Imported connection poke-to-pg in connections/poke_to_pg/configuration.yaml. State stored in connections/poke_to_pg/state_b06c6fbb-cadd-4c5c-bdbb-710add7dedb9.yaml
```

You know have local configuration files for all Airbyte resources that were already existing.
You need to edit any secret values that exist in these configuration files as secrets are not imported.
You can edit the configuration files and run `octavia apply` to continue managing them with octavia-cli.

#### `octavia import destination <DESTINATION_ID> or <DESTINATION_NAME>`

Import an existing destination to manage it with octavia-cli. You can use a destination ID or name.

| **Argument**       | **Description**       |
| ------------------ | --------------------- |
| `DESTINATION_ID`   | The destination id.   |
| `DESTINATION_NAME` | The destination name. |

#### `octavia import source <SOURCE_ID> or <SOURCE_NAME>`

Import an existing source to manage it with octavia-cli. You can use a source ID or name.

| **Argument**  | **Description**  |
| ------------- | ---------------- |
| `SOURCE_ID`   | The source id.   |
| `SOURCE_NAME` | The source name. |

**Examples**:

```bash
$ octavia import source poke
🐙 - Octavia is targetting your Airbyte instance running at http://localhost:8000 on workspace 75658e4f-e5f0-4e35-be0c-bdad33226c94.
✅ - Imported source poke in sources/poke/configuration.yaml. State stored in sources/poke/state_75658e4f-e5f0-4e35-be0c-bdad33226c94.yaml
⚠️  - Please update any secrets stored in sources/poke/configuration.yaml
```

You know have local configuration file for an Airbyte source that was already existing.
You need to edit any secret value that exist in this configuration as secrets are not imported.
You can edit the configuration and run `octavia apply` to continue managing it with octavia-cli.

#### `octavia import destination <DESTINATION_ID> or <DESTINATION_NAME>`

Import an existing destination to manage it with octavia-cli. You can use a destination ID or name.

| **Argument**       | **Description**       |
| ------------------ | --------------------- |
| `DESTINATION_ID`   | The destination id.   |
| `DESTINATION_NAME` | The destination name. |

**Examples**:

```bash
$ octavia import destination pg
🐙 - Octavia is targetting your Airbyte instance running at http://localhost:8000 on workspace 75658e4f-e5f0-4e35-be0c-bdad33226c94.
✅ - Imported destination pg in destinations/pg/configuration.yaml. State stored in destinations/pg/state_75658e4f-e5f0-4e35-be0c-bdad33226c94.yaml
⚠️  - Please update any secrets stored in destinations/pg/configuration.yaml
```

You know have local configuration file for an Airbyte destination that was already existing.
You need to edit any secret value that exist in this configuration as secrets are not imported.
You can edit the configuration and run `octavia apply` to continue managing it with octavia-cli.

#### `octavia import connection <CONNECTION_ID> or <CONNECTION_NAME>`

Import an existing connection to manage it with octavia-cli. You can use a connection ID or name.

| **Argument**      | **Description**      |
| ----------------- | -------------------- |
| `CONNECTION_ID`   | The connection id.   |
| `CONNECTION_NAME` | The connection name. |

**Examples**:

```bash
$ octavia import connection poke-to-pg
🐙 - Octavia is targetting your Airbyte instance running at http://localhost:8000 on workspace 75658e4f-e5f0-4e35-be0c-bdad33226c94.
✅ - Imported connection poke-to-pg in connections/poke-to-pg/configuration.yaml. State stored in connections/poke-to-pg/state_75658e4f-e5f0-4e35-be0c-bdad33226c94.yaml
⚠️  - Please update any secrets stored in connections/poke-to-pg/configuration.yaml
```

You know have local configuration file for an Airbyte connection that was already existing.
**N.B.: You first need to import the source and destination used by the connection.**
You can edit the configuration and run `octavia apply` to continue managing it with octavia-cli.

#### `octavia generate source <DEFINITION_ID> <SOURCE_NAME>`

Generate a YAML configuration for a source.
The YAML file will be stored at `./sources/<resource_name>/configuration.yaml`.

| **Argument**    | **Description**                                                                               |
| --------------- | --------------------------------------------------------------------------------------------- |
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
| ------------------ | ------------------------------------------------------------------------------------------------------- |
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
| --------------- | ------------ | ------------------------------------------------------------------------------------------ |
| `--source`      | Yes          | Path to the YAML configuration file of the source you want to create a connection from.    |
| `--destination` | Yes          | Path to the YAML configuration file of the destination you want to create a connection to. |

| **Argument**      | **Description**                                          |
| ----------------- | -------------------------------------------------------- |
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

| **Option** | **Required** | **Description**                                                    |
| ---------- | ------------ | ------------------------------------------------------------------ |
| `--file`   | No           | Path to the YAML configuration files you want to create or update. |
| `--force`  | No           | Run update without prompting for changes validation.               |

**Example**:

```bash
$ octavia apply
🐙 - weather exists on your Airbyte instance, let's check if we need to update it!
👀 - Here's the computed diff (🚨 remind that diff on secret fields are not displayed):
  E - Value of root['lat'] changed from "46.7603" to "45.7603".
❓ - Do you want to update weather? [y/N]: y
✍️ - Running update because a diff was detected between local and remote resource.
🎉 - Successfully updated weather on your Airbyte instance!
💾 - New state for weather stored at ./sources/weather/state_<workspace_id>.yaml.
🐙 - my_db exists on your Airbyte instance, let's check if we need to update it!
😴 - Did not update because no change detected.
🐙 - weather_to_pg exists on your Airbyte instance, let's check if we need to update it!
👀 - Here's the computed diff (🚨 remind that diff on secret fields are not displayed):
  E - Value of root['schedule']['timeUnit'] changed from "days" to "hours".
❓ - Do you want to update weather_to_pg? [y/N]: y
✍️ - Running update because a diff was detected between local and remote resource.
🎉 - Successfully updated weather_to_pg on your Airbyte instance!
💾 - New state for weather_to_pg stored at ./connections/weather_to_pg/state_<workspace_id>.yaml.
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
6. Run the unittest suite: `pytest --cov=octavia_cli`. Note, a local version of airbyte needs to be running (e.g. `docker compose up` from the root directory of the project)
7. Make sure the build passes (step 0) before opening a PR.

## Telemetry

This CLI has some telemetry tooling to send Airbyte some data about the usage of this tool.
We will use this data to improve the CLI and measure its adoption.
The telemetry sends data about:

- Which command was run (not the arguments or options used).
- Success or failure of the command run and the error type (not the error payload).
- The current Airbyte workspace id if the user has not set the _anonymous data collection_ on their Airbyte instance.

You can disable telemetry by setting the `OCTAVIA_ENABLE_TELEMETRY` environment variable to `False` or using the `--disable-telemetry` flag.

## Changelog

| Version | Date       | Description                                                                           | PR                                                          |
|---------| ---------- | ------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| 0.41.0  | 2022-10-13 | Use Basic Authentication for making API requests                                      | [#17982](https://github.com/airbytehq/airbyte/pull/17982)   |
| 0.40.0  | 2022-08-10 | Enable cron and basic scheduling                                                      | [#15253](https://github.com/airbytehq/airbyte/pull/15253)   |
| 0.39.33 | 2022-07-05 | Add `octavia import all` command                                                      | [#14374](https://github.com/airbytehq/airbyte/pull/14374)   |
| 0.39.32 | 2022-06-30 | Create import command to import and manage existing Airbyte resource from octavia-cli | [#14137](https://github.com/airbytehq/airbyte/pull/14137)   |
| 0.39.27 | 2022-06-24 | Create get command to retrieve resources JSON representation                          | [#13254](https://github.com/airbytehq/airbyte/pull/13254)   |
| 0.39.19 | 2022-06-16 | Allow connection management on multiple workspaces                                    | [#13070](https://github.com/airbytehq/airbyte/pull/12727)   |
| 0.39.19 | 2022-06-15 | Allow users to set custom HTTP headers                                                | [#12893](https://github.com/airbytehq/airbyte/pull/12893)   |
| 0.39.14 | 2022-05-12 | Enable normalization on connection                                                    | [#12727](https://github.com/airbytehq/airbyte/pull/12727)   |
| 0.37.0  | 2022-05-05 | Use snake case in connection fields                                                   | [#12133](https://github.com/airbytehq/airbyte/pull/12133)   |
| 0.35.68 | 2022-04-15 | Improve telemetry                                                                     | [#12072](https://github.com/airbytehq/airbyte/issues/11896) |
| 0.35.68 | 2022-04-12 | Add telemetry                                                                         | [#11896](https://github.com/airbytehq/airbyte/issues/11896) |
| 0.35.61 | 2022-04-07 | Alpha release                                                                         | [EPIC](https://github.com/airbytehq/airbyte/issues/10704)   |
