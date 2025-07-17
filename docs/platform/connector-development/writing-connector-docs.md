# Writing Connector Documentation

This topic guides you through writing documentation for Airbyte connectors. The systems and practices described in [Updating Documentation](../contributing-to-airbyte/writing-docs.md) apply here as well. However, there are several features and restrictions that only apply to connectors.

## QA checks

If you're writing docs for a new connector, your docs must pass our [QA checks](../contributing-to-airbyte/resources/qa-checks).

## Custom Markdown extensions for connector docs

Airbyte's connector documentation must gracefully support different contexts in a way platform documentation doesn't.

- https://docs.airbyte.com
- In-app documentation in self-managed versions of Airbyte
- In-app documentation in the Cloud version of Airbyte

Key details about setting up a connection may differ between Cloud and Self-Managed. We created custom Markdown extensions that can show or hide different pieces of content based on the reader's environment. This is a rudimentary form of a concept called single-sourcing: writing content once, but using it in multiple contexts. This prevents us from having to maintain multiple highly similar pools of content.

The following features for single-sourcing are available. You can combine them to produce a more meaningful result.

### Hide content from the Airbyte UI

Some content is important to document, but unhelpful in Airbyte's UI. This could be:

- Background information that helps people understand a connector but doesn't affect the configuration process
- Edge cases with complex solutions
- Context about each environment, which doesn't need to be seen if you're in that environment

Wrapping content in `<HideInUI>...</HideInUI>` tags prevents Airbyte from rendering that content in-app, but https://docs.airbyte.com renders it normally.

### Hide content from Cloud

You can hide content from Airbyte Cloud, while still rendering it in Self-Managed and https://docs.airbyte.com.

```md
<!-- env:oss -->

Only Self-Managed builds of the Airbyte UI will render this content.

<!-- /env:oss -->
```

### Hide content from Self-Managed

You can hide content from Airbyte Self-Managed, while still rendering it in Cloud and https://docs.airbyte.com.

```md
<!-- env:cloud -->

Only Cloud builds of the Airbyte UI will render this content.

<!-- /env:cloud -->
```

### Example

Here's an example where the configuration steps are different in Cloud and Self-Managed. In this case, you want to render everything on https://docs.airbyte.com, but you want in-app content reflect only the environment the user is running.

```markdown title="connector-doc.md"
# My connector

This content is rendered everywhere.

<!-- env:oss -->

<HideInUI>

## For open source: 

</HideInUI>

Only self-managed builds of the Airbyte UI will render this content.

<!-- /env:oss -->

<!-- env:cloud -->
<HideInUI>

## For Airbyte Cloud:

</HideInUI>

Only Cloud builds of the Airbyte UI will render this content.

<!-- /env:oss -->
```

### Testing your content

To test in-app content in [a local Airbyte build](https://docs.airbyte.com/contributing-to-airbyte/developing-locally/#develop-on-airbyte-webapp), check out the `airbyte` git repository to the same branch and directory as the airbyte platform repository. Development builds fetch connector documentation from your local filesystem, so you can edit their content and view the rendered output in Airbyte.

To test https://docs.airbyte.com content, [build Docusaurus locally](../contributing-to-airbyte/writing-docs.md#set-up-your-environment).

## Map the UI to associated content

Sometimes a field requires more explanation than can be provided in a tooltip. In these cases, use the `<FieldAnchor>` tag to link documentation to a specific UI component.

When a user selects that field in the UI, the in-app documentation panel automatically scrolls to the related documentation, highlighting all content contained inside the `<FieldAnchor></FieldAnchor>` tag.

The `FieldAnchor` syntax accepts a modified version of `jsonpath`, without the conventional `$.` prefix. It looks like this:

```md title="example-a.md"
## Configuring Widgets

<FieldAnchor field="widget_option">

...config-related instructions here...

</FieldAnchor>
```

Taking a more complex example, you can access deeper-nested fields using `jsonpath` expressions syntax:

```md title="example-b.md"
## Configuring Unstructured Streams

<FieldAnchor field="streams.0.format[unstructured],streams.1.format[unstructured],streams.2.format[unstructured]">

...config-related instructions here...

</FieldAnchor>
```

:::note
The `FieldAnchor` tag only affects in-app content for sources and destinations. It has no effect on https://docs.airbyte.com or any platform content.
:::

How it works:

- There must be blank lines between a custom tag like `FieldAnchor` the content it wraps.
- The `field` attribute must be a valid `jsonpath` expression to one of the properties nested under `connectionSpecification.properties` in that connector's `spec.json` or `spec.yaml` file. For example, if the connector spec contains a `connectionSpecification.properties.replication_method.replication_slot`, you would mark the start of the related documentation section with `<FieldAnchor field="replication_method.replication_slot">` and its end with `</FieldAnchor>`.
- Highlight the same section for multiple fields by separating them with commas, like this: `<FieldAnchor field="replication_method.replication_slot,replication_method.queue_size">`.
- To highlight a section after the user picks an option from a `oneOf`: use a `field` prop like `path.to.field[value-of-selection-key]`, where the `value-of-selection-key` is the value of a `const` field nested inside that `oneOf`.

    For example, if the specification of the `oneOf` field is:

    ```json
    "replication_method": {
      "type": "object",
      "title": "Update Method",
      "oneOf": [
        {
          "title": "Read Changes using Binary Log (CDC)",
          "required": ["method"],
          "properties": {
            "method": {
              "type": "string",
              <!-- highlight-next-line -->
              "const": "CDC",
              "order": 0
            },
            "initial_waiting_seconds": {
              "type": "integer",
              "title": "Initial Waiting Time in Seconds (Advanced)",
            },
          }
        },
        {
          "title": "Scan Changes with User Defined Cursor",
          "required": ["method"],
          "properties": {
            "method": {
              "type": "string",
              <!-- highlight-next-line -->
              "const": "STANDARD",
              "order": 0
            }
          }
        }
      ]
    }
    ```

    The selection keys are `CDC` and `STANDARD`. Wrap a specific replication method's documentation section with a `<FieldAnchor field="replication_method[CDC]">...</FieldAnchor>` tag to highlight it if the user selects CDC replication in the UI.

### Documenting PyAirbyte usage

PyAirbyte is a Python library that allows you to run syncs within a Python script for a subset of Airbyte's connectors. Documentation around PyAirbyte connectors is automatically generated from the connector's JSON schema spec. There are a few approaches to combine full control over the documentation with automatic generation for common cases:

- If a connector:
    
    1. Is PyAirbyte-enabled (`remoteRegistries.pypi.enabled` is set in the `metadata.yaml` file of the connector), and 
    2. Has no second-level heading `Usage with PyAirbyte` in the documentation 
    
  The documentation will be automatically generated and placed above the `Changelog` section.

- By manually specifying a `Usage with PyAirbyte` section, this is disabled. The following is a good starting point for this section:

```md
<HideInUI>

## Usage with PyAirbyte

<PyAirbyteExample connector="source-google-sheets" />

<SpecSchema connector="source-google-sheets" />

</HideInUI>
```

The `PyAirbyteExample` component will generate a code example that can be run with PyAirbyte, excluding an auto-generated sample configuration based on the configuration schema. The `SpecSchema` component will generate a reference table with the connector's JSON schema spec, like a non-interactive version of the connector form in the UI. It can be used on any docs page.
