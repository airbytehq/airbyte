# TODO: Define your stream schemas
Your connector must describe the schema of each stream it can output using [JSONSchema](https://json-schema.org). 

You can describe the schema of your streams using one `.json` file per stream.
 
## Static schemas
From the `square.yaml` configuration file, you read the `.json` files in the `schemas/` directory. You can refer to a schema in your configuration file using the `schema_loader` component's `file_path` field. For example:
```
schema_loader:
  type: JsonSchema
  file_path: "./source_square/schemas/customers.json"
```
Every stream specified in the configuration file should have a corresponding `.json` schema file.

Delete this file once you're done. Or don't. Up to you :)

