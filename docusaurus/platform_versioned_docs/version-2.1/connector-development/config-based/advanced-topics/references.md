# References

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