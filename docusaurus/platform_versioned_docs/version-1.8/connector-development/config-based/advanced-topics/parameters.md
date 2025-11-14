# Parameters

Parameters can be passed down from a parent component to its subcomponents using the $parameters key.
This can be used to avoid repetitions.

Schema:

```yaml
"$parameters":
  type: object
  additionalProperties: true
```

Example:

```yaml
outer:
  $parameters:
    MyKey: MyValue
  inner:
    k2: v2
```

This the example above, if both outer and inner are types with a "MyKey" field, both of them will evaluate to "MyValue".

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

In this example, "outer.MyKey" will evaluate to "MyValue", and "inner.MyKey" will evaluate to "YourValue".

The value can also be used for string interpolation:

```yaml
outer:
  $parameters:
    MyKey: MyValue
  inner:
    k2: "MyKey is {{ parameters['MyKey'] }}"
```

In this example, outer.inner.k2 will evaluate to "MyKey is MyValue"