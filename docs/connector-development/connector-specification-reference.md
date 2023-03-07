# Connector Specification Reference

The [connector specification](../understanding-airbyte/airbyte-protocol.md#spec) describes what inputs can be used to configure a connector. Like the rest of the Airbyte Protocol, it uses [JsonSchema](https://json-schema.org), but with some slight modifications.

## Demoing your specification

While iterating on your specification, you can preview what it will look like in the UI in realtime by following the instructions [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-webapp/docs/HowTo-ConnectionSpecification.md).


### Secret obfuscation

By default, any fields in a connector's specification are visible can be read in the UI. However, if you want to obfuscate fields in the UI and API \(for example when working with a password\), add the `airbyte_secret` annotation to your connector's `spec.json` e.g:

```text
"password": {
  "type": "string",
  "examples": ["hunter2"],
  "airbyte_secret": true
},
```

Here is an example of what the password field would look like: ![Screen Shot 2021-08-04 at 11 15 04 PM](https://user-images.githubusercontent.com/6246757/128300633-7f379b05-5f4a-46e8-ad88-88155e7f4260.png)


### Ordering fields in the UI

Use the `order` property inside a definition to determine the order in which it will appear relative to other objects on the same level of nesting in the UI. 

For example, using the following spec: 

```
{
  "username": {"type": "string", "order": 1},
  "password": {"type": "string", "order": 2},
  "cloud_provider": {
    "order": 0,
    "type": "object",
    "properties" : {
      "name": {"type": "string", "order": 0},
      "region": {"type": "string", "order": 1}
    }
  }
}
```

will result in the following configuration on the UI: 

![Screen Shot 2021-11-18 at 7 14 04 PM](https://user-images.githubusercontent.com/6246757/142558797-135f6c73-f05d-479f-9d88-e20cae85870c.png)


:::info

Within an object definition, if some fields have the `order` property defined, and others don't, then the fields without the `order` property defined should be rendered last in the UI. Among those elements (which don't have `order` defined), no ordering is guaranteed. 

:::


### Multi-line String inputs

Sometimes when a user is inputting a string field into a connector, newlines need to be preserveed. For example, if we want a connector to use an RSA key which looks like this:

```text
---- BEGIN PRIVATE KEY ----
123
456
789
---- END PRIVATE KEY ----
```

we need to preserve the line-breaks. In other words, the string `---- BEGIN PRIVATE KEY ----123456789---- END PRIVATE KEY ----` is not equivalent to the one above since it loses linebreaks.

By default, string inputs in the UI can lose their linebreaks. In order to accept multi-line strings in the UI, annotate your string field with `multiline: true` e.g:

```text
"private_key": {
  "type": "string",
  "description": "RSA private key to use for SSH connection",
  "airbyte_secret": true,
  "multiline": true
},
```

this will display a multi-line textbox in the UI like the following screenshot: ![Screen Shot 2021-08-04 at 11 13 09 PM](https://user-images.githubusercontent.com/6246757/128300404-1dc35323-bceb-4f93-9b81-b23cc4beb670.png)

### Hiding inputs in the UI
In some rare cases, a connector may wish to expose an input that is not available in the UI, but is still potentially configurable when running the connector outside of Airbyte, or via the UI. For example, exposing a very technical configuration like the page size of an outgoing HTTP requests may only be relevant to power users, and therefore shouldn't be available via the UI but might make sense to expose via the API. 

In this case, use the `"airbyte_hidden": true` keyword to hide that field from the UI. E.g: 

```
{
  "first_name": {
    "type": "string",
    "title": "First Name"
  },
  "secret_name": {
    "type": "string",
    "title": "You can't see me!!!",
    "airbyte_hidden": true
  }
}
```

Results in the following form:

![hidden fields](../.gitbook/assets/spec_reference_hidden_field_screenshot.png)


## Airbyte Modifications to `jsonschema`

### Using `oneOf`

In some cases, a connector needs to accept one out of many options. For example, a connector might need to know the compression codec of the file it will read, which will render in the Airbyte UI as a list of the available codecs. In JSONSchema, this can be expressed using the [oneOf](https://json-schema.org/understanding-json-schema/reference/combining.html#oneof) keyword.

:::info

Some connectors may follow an older format for dropdown lists, we are currently migrating away from that to this standard.

:::

In order for the Airbyte UI to correctly render a specification, however, a few extra rules must be followed:

1. The top-level item containing the `oneOf` must have `type: object`.
2. Each item in the `oneOf` array must be a property with `type: object`.
3. One `string` field with the same property name must be consistently present throughout each object inside the `oneOf` array. It is required to add a [`const`](https://json-schema.org/understanding-json-schema/reference/generic.html#constant-values) value unique to that `oneOf` option.

Let's look at the [source-file](../integrations/sources/file.md) implementation as an example. In this example, we have `provider` as a dropdown list option, which allows the user to select what provider their file is being hosted on. We note that the `oneOf` keyword lives under the `provider` object as follows:

In each item in the `oneOf` array, the `option_title` string field exists with the aforementioned `const` value unique to that item. This helps the UI and the connector distinguish between the option that was chosen by the user. This can be displayed with adapting the file source spec to this example:

```javascript
{
  "connection_specification": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "File Source Spec",
    "type": "object",
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
                "const": "HTTPS: Public Web",
                "order": 0
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
                "const": "GCS: Google Cloud Storage",
                "order": 0
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

### Using `enum`

In regular `jsonschema`, some drafts enforce that `enum` lists must contain distinct values, while others do not. For consistency, Airbyte enforces this restriction.

For example, this spec is invalid, since `a_format` is listed twice under the enumerated property `format`:

```javascript
{
  "connection_specification": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "File Source Spec",
    "type": "object",
    "required": ["format"],
    "properties": {
      "dataset_name": {
        ...
      },
      "format": {
        type: "string",
        enum: ["a_format", "another_format", "a_format"]
      },
    }
  }
}
```
