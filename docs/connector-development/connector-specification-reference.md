# Connector Specification Reference
The [connector specification](../understanding-airbyte/airbyte-specification.md#spec) describes what inputs can be used to configure a connector. Like the rest of the Airbyte Protocol, it uses [JsonSchema](https://json-schema.org), but with some slight modifications.  


### Using `oneOf`s 
In some cases, a connector needs to accept one out of many options. For example, a connector might need to know the compression codec of the file it will read, which will render in the Airbyte UI as a list of the available codecs. In JSONSchema, this can be expressed using the [oneOf](https://json-schema.org/understanding-json-schema/reference/combining.html#oneof) keyword.

{% hint style="info" %}
Some connectors may follow an older format for dropdown lists, we are currently migrating away from that to this standard.
{% endhint %}

In order for the Airbyte UI to correctly render a specification, however, a few extra rules must be followed: 

1. The top-level item containing the `oneOf` must have `type: object`.
2. Each item in the `oneOf` array must be a property with `type: object`.
3. One `string` field with the same property name must be consistently present throughout each object inside the `oneOf` array. It is required to add a [`const`](https://json-schema.org/understanding-json-schema/reference/generic.html#constant-values) value unique to that `oneOf` option.

Let's look at the [source-file](../integrations/sources/file.md) implementation as an example. In this example, we have `provider` as a dropdown
list option, which allows the user to select what provider their file is being hosted on. We note that the `oneOf` keyword lives under the `provider` object as follows:

In each item in the `oneOf` array, the `option_title` string field exists with the aforementioned `const` value unique to that item. This helps the UI and the connector distinguish between the option that was chosen by the user. This can
be displayed with adapting the file source spec to this example:

```json
{
  "connection_specification": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "File Source Spec",
    "type": "object",
    "additionalProperties": false,
    "required": ["dataset_name", "format", "url", "provider"],
    "properties": {
      "dataset_name": {
        ...
      },
      "format": {
        ...
      },
      "reader_options": {
        ...
      },
      "url": {
        ...
      },
      "provider": {
        "type": "object",
        "oneOf": [
          {
            "required": [
              "option_title"
            ],
            "properties": {
              "option_title": {
                "type": "string",
                "const": "HTTPS: Public Web"
              }
            }
          },
          {
            "required": [
              "option_title"
            ],
            "properties": {
              "option_title": {
                "type": "string",
                "const": "GCS: Google Cloud Storage"
              },
              "service_account_json": {
                "type": "string",
                "description": "In order to access private Buckets stored on Google Cloud, this connector would need a service account json credentials with the proper permissions as described <a href=\"https://cloud.google.com/iam/docs/service-accounts\" target=\"_blank\">here</a>. Please generate the credentials.json file and copy/paste its content to this field (expecting JSON formats). If accessing publicly available data, this field is not necessary."
              }
            }
          }
        ]
      }
  }
} 
```

