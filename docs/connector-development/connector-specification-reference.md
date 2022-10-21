# Connector Specification Reference

The [connector specification](../understanding-airbyte/airbyte-protocol.md#spec) describes what inputs can be used to configure a connector.
The connector specification uses YAML syntax to build the configuration.

This is an empty specification. It has some fields used by Airbyte to display the guide during setup and other additional properties.

```yaml
documentationUrl: https://docs.airbyte.io/integrations/sources/example
connectionSpecification:
  $schema: http://json-schema.org/draft-07/schema#
  title: Example Spec
  type: object
  required:
    - api_key
  additionalProperties: true
  properties:
    {}
```

### Types 
Each property must have a `type`. The speficiation allows you to use string, integer, number, boolean and array.
You can also use the object type to create more complex structures which will be described later, see Using `oneOf`s section. 
Also properties have a title and description and examples.

Let's start building our example configuration:

```yaml
properties:
  api_key:
    type: string
    title: API Key
    description:  The API key generated following the instructions in the docs
  max_request_per_minute:
    type: integer
    title: Maximum Requests per Minute
    description: >-
      The maximum request your account allow to request to Example API.
      Check the <a href="https://docs.example.com/max-request-per-minute">docs</a>.
      You can use reference links using the example above.
  categories_to_remove:
    type: array
    title: Categories to Remove from Reports
    description: Check all categories in the documentation
    examples:
      - blue
      - green
      - red
  sandbox:
    type: boolean
    title: Sandbox Account
    description: If your account is using sandbox endpoint or production one.
```

### Use of the Default value
...
### Secret obfuscation

By default, any fields in a connector's specification are visible can be read in the UI. However, if you want to obfuscate fields in the UI and API \(for example when working with a password\), add the `airbyte_secret` annotation to your connector's `spec.yaml` e.g:

```yaml
  api_key:
    type: string
    title: API Key
    description:  The API key generated following the instructions in the docs
    airbyte_secret: true
```

### Ordering fields in the UI

Use the `order` property inside a definition to determine the order in which it will appear relative to other objects on the same level of nesting in the UI. 

For example, using the following spec: 

```yaml
properties:
  api_key:
    type: string
    order: 0
  max_request_per_minute:
    type: integer
    order: 1
  categories_to_remove:
    type: array
    order: 2
  sandbox:
    type: boolean
    order: 3
  region: 
    type: string
    order: 4
```
### Restrict Inputs using Pattern Match
...

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

```yaml
private_key:
  type: string
  description: RSA private key to use for SSH connection
  airbyte_secret: true
  multiline": true
```

this will display a multi-line textbox in the UI like the following screenshot: ![Screen Shot 2021-08-04 at 11 13 09 PM](https://user-images.githubusercontent.com/6246757/128300404-1dc35323-bceb-4f93-9b81-b23cc4beb670.png)

### Using Enum 
...

### Datetime Inputs
...
### Hiding Inputs in the UI
In some rare cases, a connector may wish to expose an input that is not available in the UI, but is still potentially configurable when running the connector outside of Airbyte, or via the UI. For example, exposing a very technical configuration like the page size of an outgoing HTTP requests may only be relevant to power users, and therefore shouldn't be available via the UI but might make sense to expose via the API. 

In this case, use the `"airbyte_hidden": true` keyword to hide that field from the UI. E.g: 

```yaml
properties:
  api_key:
    type: string
    order: 0
  max_request_per_minute:
    type: integer
    order: 1
  categories_to_remove:
    type: array
    order: 2
  sandbox:
    type: boolean
    order: 3
  page_size:
    type: integer
    title: Page Size
    description: The number of records retrieve by each request.
    default: 100
    airbyte_hidden: true
```

![hidden fields](../.gitbook/assets/spec_reference_hidden_field_screenshot.png)


### Using `oneOf`s

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

```yaml
credentials:
  type: object
  title: Authentication
  description: Credentials for connecting to the Example Connector
  oneOf:
   - title: Authenticate via Example (OAuth)
     type: object
     required:
       - auth_type
       - api_key
     properties:
        auth_type:
          type: string
          const: APIKEY
        api_key:
          title: API Key
          type: string
   - title: Service Account Key Authentication
     type: object
     required:
       - auth_type
       - username
       - password
     properties:
        auth_type:
          type: string
          const: USERNAME
        username:
          type: string
          title: Service Account Information.
          description: Enter your Service Account
        password:
          type: string
          title: Another Parameter.
          pattern: 
```
