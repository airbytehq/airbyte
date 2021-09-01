# openapi2jsonschema
Util for generating catalog schema from OpenAPI definition file. Froked from [openapi2jsonschema](https://github.com/instrumenta/openapi2jsonschema) util with fixes for generating standlone schemas e.g. ones that don't contain reference to another files/resources.

## Usage
```bash
$ tools/openapi2jsonschema/run.sh <path to OpenAPI definition file>
```
It would  generate set of jsonschema files based on components described on OpenAPI definition and place it on "**schemas**" fodler in current working directory.

 Support OpenAPI v2.0, v3.0 and v3.1. Works with both json and yaml OpenAPI formats.

### Examples
You can try to run this tool on sample OpenApi definition files located in [exmaples](./examples) directory. That is some OpenAPI files taken from APIs-guru repo [from github](https://github.com/APIs-guru).