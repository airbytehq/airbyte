# Connector definition

Connectors are defined as a yaml configuration describing the connector's Source.

3 top-level fields are required:

1. `streams`: List of streams that are part of the source
2. `check`: Component describing how to check the connection.
3. `version`: The framework version.

The configuration will be validated against this JSON Schema, which defines the set of valid properties.

The general structure of the YAML is as follows:

```yaml
version: "0.1.0"
definitions:
  <key-value pairs defining objects which will be reused in the YAML connector>
streams:
  <list stream definitions>
check:
  <definition of connection checker>
```

We recommend using the `Configuration Based Source` template from the template generator in `airbyte-integrations/connector-templates/generator` to generate the basic file structure.

See the [tutorial for a complete connector definition](tutorial/6-testing.md)

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

If the component is a mapping with a "class_name" field,
an object of type "class_name" will be instantiated by passing the mapping's other fields to the constructor

```yaml
my_component:
  class_name: "fully_qualified.class_name"
  a_parameter: 3
  another_parameter: "hello"
```

will result in

```
fully_qualified.class_name(a_parameter=3, another_parameter="hello")
```

If the component definition is a mapping with a "type" field,
the factory will lookup the [CLASS_TYPES_REGISTRY](https://github.com/airbytehq/airbyte/blob/master/airbyte-cdk/python/airbyte_cdk/sources/declarative/parsers/class_types_registry.py) and replace the "type" field by "class_name" -> CLASS_TYPES_REGISTRY[type]
and instantiate the object from the resulting mapping

If the component definition is a mapping with neither a "class_name" nor a "type" field,
the factory will do a best-effort attempt at inferring the component type by looking up the parent object's constructor type hints.
If the type hint is an interface present in [DEFAULT_IMPLEMENTATIONS_REGISTRY](https://github.com/airbytehq/airbyte/blob/master/airbyte-cdk/python/airbyte_cdk/sources/declarative/parsers/default_implementation_registry.py,
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

### $options

Parameters can be passed down from a parent component to its subcomponents using the $options key.
This can be used to avoid repetitions.

```yaml
outer:
  $options:
    MyKey: MyValue
  inner:
    k2: v2
```

This the example above, if both outer and inner are types with a "MyKey" field, both of them will evaluate to "MyValue".

These parameters can be overwritten by subcomponents as a form of specialization:

```yaml
outer:
  $options:
    MyKey: MyValue
  inner:
    $options:
      MyKey: YourValue
    k2: v2
```

In this example, "outer.MyKey" will evaluate to "MyValue", and "inner.MyKey" will evaluate to "YourValue".

The value can also be used for string interpolation:

```yaml
outer:
  $options:
    MyKey: MyValue
  inner:
    k2: "MyKey is {{ options['MyKey'] }}"
```

In this example, outer.inner.k2 will evaluate to "MyKey is MyValue"

## References

Strings can contain references to previously defined values.
The parser will dereference these values to produce a complete object definition.

References can be defined using a "*ref({arg})" string.

```yaml
key: 1234
reference: "*ref(key)"
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
same_key_value_pairs: "*ref(key_value_pairs)"
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
  $ref: "*ref(key_value_pairs)"
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
Nested references are ambiguous because one could define a key containing with `.`
in this example, we want to refer to the limit key in the dict object:

```yaml
dict:
  limit: 50
limit_ref: "*ref(dict.limit)"
```

will produce the following definition:

```yaml
dict
limit: 50
limit-ref: 50
```

whereas here we want to access the `nested.path` value.

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
nested.path: "uh oh"
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
the "options" keyword [see ($options)](yaml-structure.md#object-instantiation) can be referenced.

For example, some_object.inner_object.key will evaluate to "Hello airbyte" at runtime.

```yaml
some_object:
  $options:
    name: "airbyte"
  inner_object:
    key: "Hello {{ options.name }}"
```

Some components also pass in additional arguments to the context.
This is the case for the [record selector](record-selector.md), which passes in an additional `response` argument.

Both dot notation and bracket notations (with single quotes ( `'`)) are interchangeable.
This means that both these string templates will evaluate to the same string:

1. `"{{ options.name }}"`
2. `"{{ options['name'] }}"`

In additional to passing additional values through the $options argument, macros can be called from within the string interpolation.
For example,
`"{{ max(2, 3) }}" -> 3`

The macros available can be found [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-cdk/python/airbyte_cdk/sources/declarative/interpolation/macros.py).

Additional information on jinja templating can be found at https://jinja.palletsprojects.com/en/3.1.x/templates/#

## Component schema reference

A JSON schema representation of the relationships between the components that can be used in the YAML configuration can be found [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-cdk/python/airbyte_cdk/sources/declarative/config_component_schema.json).