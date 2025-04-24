# Schema Generator

Util for generating catalog schema from a connector `read` command output.

## Prerequisites

To use this tool you first need to:

- Define all your streams.
- Create schema files for each stream, containing only `{}` (valid json files). See
  [this doc section](https://docs.airbyte.com/connector-development/cdk-python/schemas#static-schemas)
  for instructions on how to name these files.

Going through all the steps above should enable you to run the `read` command of your connector
using the docker image, which is the input for this tool.

## Usage

First install the tools in it's own virtual environment:

```bash
$ cd tools/schema_generator # assumes you are starting from the root of the Airbyte project.
$ poetry install
```

To use a connector's `run` command we first need a `ConfiguredAirbyteCatalog`:

```bash
$ ../../airbyte-integrations/connectors/<your-connector> # you need to use the tool at the root folder of a connector
$ docker run --rm -v $(pwd)/secrets:/secrets airbyte/<your-connector-image-name>:dev discover --config /secrets/config.json | schema_generator --configure-catalog
```

This will created the file **configured_catalog.json** in the **integration_tests** folder in the
current working directory.

Now you're all set to run the following command and generate your schemas:

```bash
$ docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/<your-connector-image-name>:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json | schema_generator --infer-schemas
```

Which will create schema files for all streams and place them in the **schemas** folder in the
current working directory.
