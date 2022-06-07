# Schema Generator
Util for generating catalog schema from a connector `read` command output.

## Usage

First install the tools in it's own virtual environment:

```bash
$ cd tools/schema_generator # assumes you are starting from the root of the Airbyte project.
$ python -m venv .venv # Create a virtual environment in the .venv directory
$ source .venv/bin/activate # enable the venv
$ python setup.py install
```

To use a connectors `run` command we first need an AirbyteConfiguredCatalog:

```bash
$ cd ../../connectors/<your-connector> # you need to use the tool at the root folder of a connector
$ docker run --rm -v $(pwd)/secrets:/secrets airbyte/<your-connector-image-name>:dev discover --config /secrets/config.json | schema_generator --configure-catalog
```
This will created the file **configured_catalog.json** in the **integration_tests** folder in the current working directory.

Now you're all set to run the following command and generate your schemas:

```bash
$ docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/<your-connector-image-name>:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json | schema_generator --infer-schemas
```
Which will create schema files for all streams and place them in the **schemas** folder in the current working directory.
