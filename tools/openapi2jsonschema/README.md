# openapi2jsonschema

Util for generating catalog schema from OpenAPI definition file. Forked from [openapi2jsonschema](https://github.com/instrumenta/openapi2jsonschema) util with fixes for generating standlone schemas e.g. ones that don't contain reference to other files/resources.

## Usage

```bash
$ tools/openapi2jsonschema/run.sh <path to OpenAPI definition file>
```

It would generate set of JSONSchema files based on components described on OpenAPI's definition and place it in "**schemas**" folder in the current working directory.

Support OpenAPI v2.0, v3.0 and v3.1. Works with both JSON and Yaml OpenAPI formats.

### Examples

You can try to run this tool on the sample OpenApi definition files located in [examples](./examples) directory. There are some OpenAPI files taken from APIs-guru repo [from github](https://github.com/APIs-guru).
