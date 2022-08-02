# Connector definition

Connectors are defined as a yaml configuration describing the connector's Source.

2 top-level fields are required:

1. `streams`: list of streams that are part of the source
2. `check`: component describing how to check the connection.

The configuration will be validated against this JSON Schema, which defines the set of valid properties.

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

```
{
  "class_name": "fully_qualified.class_name",
  "a_parameter: 3,
  "another_parameter: "hello"
}
```

will result in

```
fully_qualified.class_name(a_parameter=3, another_parameter="helo"
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

Parameters can be passed down from a parent component to its subcomponents using the $options key.
This can be used to avoid repetitions.

```
outer:
  $options:
    MyKey: MyValue
  inner:
   k2: v2
```

This the example above, if both outer and inner are types with a "MyKey" field, both of them will evaluate to "MyValue".

The value can also be used for string interpolation:

```
outer:
  $options:
    MyKey: MyValue
  inner:
   k2: "MyKey is {{ options.MyKey }}"
```

In this example, outer.inner.k2 will evaluate to "MyValue"

More details on object instantiation can be found [here](https://airbyte-cdk.readthedocs.io/en/latest/api/airbyte_cdk.sources.declarative.parsers.html?highlight=factory#airbyte_cdk.sources.declarative.parsers.factory.DeclarativeComponentFactory).

## References

Strings can contain references to values previously defined.
The parser will dereference these values to produce a complete ConnectionDefinition

References can be defined using a *ref(<arg>) string.

```
key: 1234
reference: "*ref(key)"
```

will produce the following definition:

```
key: 1234
reference: 1234
```

This also works with objects:

```
key_value_pairs:
  k1: v1
  k2: v2
same_key_value_pairs: "*ref(key_value_pairs)"
```

will produce the following definition:

```
key_value_pairs:
  k1: v1
  k2: v2
same_key_value_pairs:
  k1: v1
  k2: v2
```

The $ref keyword can be used to refer to an object and enhance it with addition key-value pairs

```
key_value_pairs:
  k1: v1
  k2: v2
same_key_value_pairs:
  $ref: "*ref(key_value_pairs)"
  k3: v3
```

will produce the following definition:

```
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

```
dict:
    limit: 50
limit_ref: "*ref(dict.limit)"
```

will produce the following definition:

```
dict
    limit: 50
limit-ref: 50
```

whereas here we want to access the `nested.path` value.

```
nested:
    path: "first one"
nested.path: "uh oh"
value: "ref(nested.path)
```

will produce the following definition:

```
nested:
    path: "first one"
nested.path: "uh oh"
value: "uh oh"
```

to resolve the ambiguity, we try looking for the reference key at the top level, and then traverse the structs downward
until we find a key with the given path, or until there is nothing to traverse.

More details on referencing values can be found [here](https://airbyte-cdk.readthedocs.io/en/latest/api/airbyte_cdk.sources.declarative.parsers.html?highlight=yamlparser#airbyte_cdk.sources.declarative.parsers.yaml_parser.YamlParser).