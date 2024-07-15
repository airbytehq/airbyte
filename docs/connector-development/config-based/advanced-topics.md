# Advanced Topics

## Object instantiation

This section describes the object that are to be instantiated from the YAML definition.

If the component is a literal, then it is returned as is:

```
3
```

will result in

```
3
```

If the component definition is a mapping with a "type" field,
the factory will lookup the [CLASS_TYPES_REGISTRY](https://github.com/airbytehq/airbyte/blob/master/airbyte-cdk/python/airbyte_cdk/sources/declarative/parsers/class_types_registry.py) and replace the "type" field by "class_name" -> CLASS_TYPES_REGISTRY[type]
and instantiate the object from the resulting mapping

If the component definition is a mapping with neither a "class_name" nor a "type" field,
the factory will do a best-effort attempt at inferring the component type by looking up the parent object's constructor type hints.
If the type hint is an interface present in [DEFAULT_IMPLEMENTATIONS_REGISTRY](https://github.com/airbytehq/airbyte/blob/master/airbyte-cdk/python/airbyte_cdk/sources/declarative/parsers/default_implementation_registry.py),
then the factory will create an object of its default implementation.

If the component definition is a list, then the factory will iterate over the elements of the list,
instantiate its subcomponents, and return a list of instantiated objects.

If the component has subcomponents, the factory will create the subcomponents before instantiating the top level object

```
{
  "type": TopLevel
  "param":
    {
      "type": "ParamType"
      "k": "v"
    }
}
```

will result in

```
TopLevel(param=ParamType(k="v"))
```

More details on object instantiation can be found [here](https://airbyte-cdk.readthedocs.io/en/latest/api/airbyte_cdk.sources.declarative.parsers.html?highlight=factory#airbyte_cdk.sources.declarative.parsers.factory.DeclarativeComponentFactory).

## $parameters

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

## References

Strings can contain references to previously defined values.
The parser will dereference these values to produce a complete object definition.

References can be defined using a `#/{arg}` string.

```yaml
key: 1234
reference: "#/key"
```

will produce the following definition:

```yaml
key: 1234
reference: 1234
```

This also works with objects:

```yaml
key_value_pairs:
  k1: v1
  k2: v2
same_key_value_pairs: "#/key_value_pairs"
```

will produce the following definition:

```yaml
key_value_pairs:
  k1: v1
  k2: v2
same_key_value_pairs:
  k1: v1
  k2: v2
```

The $ref keyword can be used to refer to an object and enhance it with addition key-value pairs

```yaml
key_value_pairs:
  k1: v1
  k2: v2
same_key_value_pairs:
  $ref: "#/key_value_pairs"
  k3: v3
```

will produce the following definition:

```yaml
key_value_pairs:
  k1: v1
  k2: v2
same_key_value_pairs:
  k1: v1
  k2: v2
  k3: v3
```

References can also point to nested values.
Nested references are ambiguous because one could define a key containing with `/`
in this example, we want to refer to the limit key in the dict object:

```yaml
dict:
  limit: 50
limit_ref: "#/dict/limit"
```

will produce the following definition:

```yaml
dict
limit: 50
limit-ref: 50
```

whereas here we want to access the `nested/path` value.

```yaml
nested:
  path: "first one"
nested.path: "uh oh"
value: "ref(nested.path)
```

will produce the following definition:

```yaml
nested:
  path: "first one"
nested/path: "uh oh"
value: "uh oh"
```

To resolve the ambiguity, we try looking for the reference key at the top-level, and then traverse the structs downward
until we find a key with the given path, or until there is nothing to traverse.

More details on referencing values can be found [here](https://airbyte-cdk.readthedocs.io/en/latest/api/airbyte_cdk.sources.declarative.parsers.html?highlight=yamlparser#airbyte_cdk.sources.declarative.parsers.yaml_parser.YamlParser).

## String interpolation

String values can be evaluated as Jinja2 templates.

If the input string is a raw string, the interpolated string will be the same.
`"hello world" -> "hello world"`

The engine will evaluate the content passed within `{{...}}`, interpolating the keys from context-specific arguments.
The "parameters" keyword [see ($parameters)](#parameters) can be referenced.

For example, some_object.inner_object.key will evaluate to "Hello airbyte" at runtime.

```yaml
some_object:
  $parameters:
    name: "airbyte"
  inner_object:
    key: "Hello {{ parameters.name }}"
```

Some components also pass in additional arguments to the context.
This is the case for the [record selector](./understanding-the-yaml-file/record-selector.md), which passes in an additional `response` argument.

Both dot notation and bracket notations (with single quotes ( `'`)) are interchangeable.
This means that both these string templates will evaluate to the same string:

1. `"{{ parameters.name }}"`
2. `"{{ parameters['name'] }}"`

In addition to passing additional values through the $parameters argument, macros can be called from within the string interpolation.
For example,
`"{{ max(2, 3) }}" -> 3`

The macros and variables available in all possible contexts are documented in the [YAML Reference](./understanding-the-yaml-file/reference.md#variables).

Additional information on jinja templating can be found at [https://jinja.palletsprojects.com/en/3.1.x/templates/#](https://jinja.palletsprojects.com/en/3.1.x/templates/#)

## Component schema reference

A JSON schema representation of the relationships between the components that can be used in the YAML configuration can be found [here](../../../airbyte-cdk/python/airbyte_cdk/sources/declarative/declarative_component_schema.yaml).

## Custom components

:::info
Please help us improve the low code CDK! If you find yourself needing to build a custom component,please [create a feature request issue](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fenhancement%2C+%2Cneeds-triage%2C+area%2Flow-code%2Fcomponents&template=feature-request.md&title=Low%20Code%20Feature:). If appropriate, we'll add it directly to the framework (or you can submit a PR)!

If an issue already exist for the missing feature you need, please upvote or comment on it so we can prioritize the issue accordingly.
:::

Any built-in components can be overloaded by a custom Python class.
To create a custom component, define a new class in a new file in the connector's module.
The class must implement the interface of the component it is replacing. For instance, a pagination strategy must implement `airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy.PaginationStrategy`.
The class must also be a dataclass where each field represents an argument to configure from the yaml file, and an `InitVar` named parameters.

For example:

```
@dataclass
class MyPaginationStrategy(PaginationStrategy):
  my_field: Union[InterpolatedString, str]
  parameters: InitVar[Mapping[str, Any]]

  def __post_init__(self, parameters: Mapping[str, Any]):
    pass

  def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
    pass

  def reset(self):
    pass
```

This class can then be referred from the yaml file by specifying the type of custom component and using its fully qualified class name:

```yaml
pagination_strategy:
  type: "CustomPaginationStrategy"
  class_name: "my_connector_module.MyPaginationStrategy"
  my_field: "hello world"
```

### Custom Components that pass fields to child components

There are certain scenarios where a child subcomponent might rely on a field defined on a parent component. For regular components, we perform this propagation of fields from the parent component to the child automatically.
However, custom components do not support this behavior. If you have a child subcomponent of your custom component that falls under this use case, you will see an error message like:

```
Error creating component 'DefaultPaginator' with parent custom component source_example.components.CustomRetriever: Please provide DefaultPaginator.$parameters.url_base
```

When you receive this error, you can address this by defining the missing field within the `$parameters` block of the child component.

```yaml
  paginator:
    type: "DefaultPaginator"
    <...>
    $parameters:
      url_base: "https://example.com"
```

## How the framework works

1. Given the connection config and an optional stream state, the `PartitionRouter` computes the partitions that should be routed to read data.
2. Iterate over all the partitions defined by the stream's partition router.
3. For each partition,
   1. Submit a request to the partner API as defined by the requester
   2. Select the records from the response
   3. Repeat for as long as the paginator points to a next page

[connector-flow](./assets/connector-flow.png)

## More readings

- [Record selector](./understanding-the-yaml-file/record-selector.md)
- [Partition routers](./understanding-the-yaml-file/partition-router.md)
- [Source schema](../../../airbyte-cdk/python/airbyte_cdk/sources/declarative/declarative_component_schema.yaml)
