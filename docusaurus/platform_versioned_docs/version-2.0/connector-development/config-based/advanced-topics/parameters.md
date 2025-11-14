# Parameters

Parameters can be passed down from a parent component to its subcomponents using the $parameters key.
This can be used to avoid repetitions.

Schema:

```yaml
"$parameters":
  type: object
  additionalProperties: true
```

## Basic Usage

Example:

```yaml
outer:
  $parameters:
    MyKey: MyValue
  inner:
    k2: v2
```

In this example, if both outer and inner are types with a "MyKey" field, both of them evaluate to "MyValue."

These parameters can be overwritten by subcomponents as a form of specialization:

```yaml
outer:
  $parameters:
    MyKey: MyValue
  inner:
    $parameters:
      MyKey: YourValue
    k2: v2
```

In this example, "outer.MyKey" evaluates to "MyValue," and "inner.MyKey" evaluates to "YourValue."

The value can also be used for string interpolation:

```yaml
outer:
  $parameters:
    MyKey: MyValue
  inner:
    k2: "MyKey is {{ parameters['MyKey'] }}"
```

In this example, outer.inner.k2 evaluates to "MyKey is MyValue."

## Automatic Parameter Propagation

Parameters are automatically applied to component fields when those fields are not explicitly set. This happens recursively through nested components, allowing you to define parameters at a high level (like a stream) and have them automatically flow down to deeply nested components (like a requester inside a retriever).

### How It Works

When a component is processed:

1. Parameters from parent components are merged with the current component's parameters
2. Each parameter key is checked against the component's fields
3. If a field with that name exists and is not already set (or evaluates to false), the parameter value is assigned to that field
4. The merged parameters are then passed down to all child components recursively

### Precedence Rules

- **Explicit values win**: If a field is explicitly set on a component, parameters do not override it
- **Child parameters override parent parameters**: Parameters defined on a child component take precedence over those from parent components
- **Exclusion rule**: When descending into a nested component, any parameter whose key matches the component's field name is temporarily excluded from propagation to avoid circular references

### Real-World Example

In the Stripe connector, multiple streams share the same base configuration but differ only in their API path. Here's how parameters enable this:

```yaml
definitions:
  base_stream:
    type: DeclarativeStream
    retriever:
      $ref: "#/definitions/base_retriever"
    # ... other common configuration

  base_retriever:
    type: SimpleRetriever
    requester:
      $ref: "#/definitions/base_requester"
    # ... other retriever configuration

  base_requester:
    type: HttpRequester
    url_base: "https://api.stripe.com/v1"
    # Note: no 'path' field defined here

streams:
  shipping_rates:
    $ref: "#/definitions/base_stream"
    $parameters:
      path: shipping_rates
      name: shipping_rates
    schema_loader:
      # ... schema configuration

  file_links:
    $ref: "#/definitions/base_stream"
    $parameters:
      path: file_links
      name: file_links
    schema_loader:
      # ... schema configuration
```

In this example:

- Both streams reference the same `base_stream` definition
- Each stream provides different `$parameters` values for `path` and `name`
- These parameters automatically propagate down through the component hierarchy: stream → retriever → requester
- The `path` parameter automatically sets the `requester.path` field, even though it's nested two levels deep
- The `name` parameter sets the `stream.name` field

This pattern eliminates repetition and makes it easy to create multiple similar streams that differ only in a few key values.

### Technical Details

The parameter propagation mechanism is implemented in the `ManifestComponentTransformer.propagate_types_and_parameters` method in the CDK. For more details, see the [CDK source code](https://github.com/airbytehq/airbyte-python-cdk/blob/main/airbyte_cdk/sources/declarative/parsers/manifest_component_transformer.py).
