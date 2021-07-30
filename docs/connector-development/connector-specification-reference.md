# Connector Specification Reference
The [connector specification](../understanding-airbyte/airbyte-specification.md#spec) describes what inputs can be used to configure a connector. Like the rest of the Airbyte Protocol, it uses [JsonSchema](https://json-schema.org), but with some slight modifications.  


### Using `oneOf`s 
In some cases, a connector needs to accept one out of many options. For example, a connector might need to know the compression codec of the file it will read. In JSONSchema, this can be expressed using the [oneOf](https://json-schema.org/understanding-json-schema/reference/combining.html#oneof) keyword.

In order for the Airbyte UI to correctly render a specification, however, a few extra rules must be followed: 

1. The top-level item containing the `oneOf` must have `type: object`.
2. Each item in the `oneOf` array must be a property with `type: object`.
3. One `string` field with the same property name must be consistently present throughout each object inside the `oneOf` array. In each instance of this field, there must be a [`const`](https://json-schema.org/understanding-json-schema/reference/generic.html#constant-values) value unique to that `oneOf` option. For example: 
    ```
    {
      "dropdown_list_option": {
        "type": "object",
        "oneOf": [
          {
            "required": ["option_title"],
            "properties": {
              "option_title": {
                "type": "string",
                "constant": "choice_1"
              }
            }
          },
          {
            "required": [
              "option_title",
              "extra_option_1"
            ],
            "properties": {
              "option_title": {
                "type": "string",
                "constant": "choice_2"
              },
              "extra_option_1": {
                // these are just "normal" JSON Schema type definitions, can be integer, object, they can have "description" and "required" fields etc...
                "title": "Extra Option 1",
                "type": "integer"
              }
            }
          }
        ]
      }
    }
    ```
    Note that in each item in the `oneOf` array, the `option_title` string field exists with a `constant` value unique to that item. This helps the UI and the connector distinguish between the option that was chosen by the user. 
