# Writing Connector Documentation

This document provides guidance on tools and techniques specifically for writing documentation for Airbyte connectors.

For more information about writing documentation at Airbyte generally, please also see the [Contributing Guide for Airbyte Documentation](../contributing-to-airbyte/writing-docs.md).

## Custom markdown extensions for connector docs

Airbyte's markdown documentation—particularly connector-specific documentation—needs to gracefully support multiple different contexts: key details may differ between open-source builds and Airbyte Cloud, and the more exhaustive explanations appropriate for https://docs.airbyte.com may bury key details when rendered as inline documentation within the Airbyte application. In order to support all these different contexts without resorting to multiple overlapping files that must be maintained in parallel, Airbyte's documentation tooling supports multiple nonstandard features.

Please familiarize yourself with all the tools available to you when writing documentation for a connector, so that you can provide appropriately tailored information to your readers in whichever context they see it.

:::note
As a general rule, features that introduce new behavior or prevent certain content from rendering will affect how the Airbyte UI displays markdown content, but have no impact on https://docs.airbyte.com. If you want to test out these in-app features in [a local Airbyte build](https://docs.airbyte.com/contributing-to-airbyte/developing-locally/#develop-on-airbyte-webapp), ensure that you have the `airbyte` git repository checked out to the same parent directory as the airbyte platform repository: if so, development builds will by default fetch connector documentation from your local filesystem, allowing you to freely edit their content and view the rendered output.
:::

## Mapping UI to Associated Docs

Sometimes a connector's configuration UI may have a field that requires more explanation than can be provided in the UI itself. In these cases, the connector developer can use the `FieldAnchor` syntax below to link documentation to a specific UI component.

When a user selects the associated field in the UI, the documentation will automatically scroll to the related documentation section the right-hand panel.

The `FieldAnchor` syntax accepts a modified `jsonpath` expression, as follows:

`example-a.md`:
```md
## Configuring Widgets

<FieldAnchor field="widget_option">

...config-related instructions here...

</FieldAnchor>
```

Taking a more complex example, you can access deeper-nested fields using `jsonpath` expressions syntax:

`example-b.md`:
```md
## Configuring Unstructures Streams

<FieldAnchor field="streams.0.format[unstructured],streams.1.format[unstructured],streams.2.format[unstructured]">

...config-related instructions here...

</FieldAnchor>
```

Note:
- The syntax expected is a modified version of jsonpath, without the conventional `$.` prefix.
- The `FieldAnchor` syntax is only supported in the context of connector documentation, and will not render on the documentation site.

How it works:

- When a user focuses the field identified by the `field` attribute in the connector setup UI, the documentation pane will automatically scroll to the associated section of the documentation, highlighting all content contained inside the `<FieldAnchor></FieldAnchor>` tag.
- These are rendered as regular divs in the documentation site, so they have no effect in places other than the in-app documentation panel.
- There must be blank lines between a custom tag like `FieldAnchor` the content it wraps for the documentation site to render markdown syntax inside the custom tag to html.
- The `field` attribute must be a valid `jsonpath` expression to one of the properties nested under `connectionSpecification.properties` in that connector's `spec.json` or `spec.yaml` file. For example, if the connector spec contains a `connectionSpecification.properties.replication_method.replication_slot`, you would mark the start of the related documentation section with `<FieldAnchor field="replication_method.replication_slot">` and its end with `</FieldAnchor>`.
- It's also possible to highlight the same section for multiple fields by separating them with commas, like `<FieldAnchor field="replication_method.replication_slot,replication_method.queue_size">`.
- To mark a section as highlighted after the user picks an option from a `oneOf`: use a `field` prop like `path.to.field[value-of-selection-key]`, where the `value-of-selection-key` is the value of a `const` field nested inside that `oneOf`. For example, if the specification of the `oneOf` field is:

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
          "const": "STANDARD",
          "order": 0
        }
      }
    }
  ]
}
```

The selection keys are `CDC` and `STANDARD`, so you can wrap a specific replication method's documentation section with a `<FieldAnchor field="replication_method[CDC]">...</FieldAnchor>` tag, and it will be highlighted if the user selects CDC replication in the UI.

:::tip
Because of their close connection with the connector setup form fields, `<FieldAnchor>` tags are only enabled for the source and destination setup pages.
:::

## Prevent specific docs from rendering in the Config UI with `<HideInUI>`

Certain content is important to document, but unhelpful in the context of the Airbyte UI's inline documentation views:

- background information that helps users understand a connector but doesn't affect configuration
- edge cases that are unusual but time-consuming to solve
- context for readers on the documentation site about environment-specific content (see [below](#environment-specific-in-app-content-with-magic-html-comments))

Wrapping such content in a pair of `<HideInUI>...</HideInUI>` tags will prevent it from being rendered within the Airbyte UI without affecting its presentation on https://docs.airbyte.com. This allows a single markdown file to be the source of truth for both a streamlined in-app reference and a more thorough treatment on the documentation website.
