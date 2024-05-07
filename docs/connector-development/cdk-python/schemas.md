# Defining Stream Schemas

Your connector must describe the schema of each stream it can output using [JSONSchema](https://json-schema.org).

The simplest way to do this is to describe the schema of your streams using one `.json` file per stream. You can also dynamically generate the schema of your stream in code, or you can combine both approaches: start with a `.json` file and dynamically add properties to it.

The schema of a stream is the return value of `Stream.get_json_schema`.

## Static schemas

By default, `Stream.get_json_schema` reads a `.json` file in the `schemas/` directory whose name is equal to the value of the `Stream.name` property. In turn `Stream.name` by default returns the name of the class in snake case. Therefore, if you have a class `class EmployeeBenefits(HttpStream)` the default behavior will look for a file called `schemas/employee_benefits.json`. You can override any of these behaviors as you need.

Important note: any objects referenced via `$ref` should be placed in the `shared/` directory in their own `.json` files.

### Generating schemas from OpenAPI definitions

If you are implementing a connector to pull data from an API which publishes an [OpenAPI/Swagger spec](https://swagger.io/specification/), you can use a tool we've provided for generating JSON schemas from the OpenAPI definition file. Detailed information can be found [here](https://github.com/airbytehq/airbyte/tree/master/tools/openapi2jsonschema/).

### Generating schemas using the output of your connector's read command

We also provide a tool for generating schemas using a connector's `read` command output. Detailed information can be found [here](https://github.com/airbytehq/airbyte/tree/master/tools/schema_generator/).

### Backwards Compatibility

Because statically defined schemas explicitly define how data is represented in a destination, updates to a schema must be backwards compatible with prior versions. More information about breaking changes can be found [here](../best-practices.md#schema-breaking-changes)

## Dynamic schemas

If you'd rather define your schema in code, override `Stream.get_json_schema` in your stream class to return a `dict` describing the schema using [JSONSchema](https://json-schema.org).

## Dynamically modifying static schemas

Override `Stream.get_json_schema` to run the default behavior, edit the returned value, then return the edited value:

```text
def get_json_schema(self):
    schema = super().get_json_schema()
    schema['dynamically_determined_property'] = "property"
    return schema
```

## Type transformation

It is important to ensure output data conforms to the declared json schema. This is because the destination receiving this data to load into tables may strictly enforce schema \(e.g. when data is stored in a SQL database, you can't put CHAR type into INTEGER column\). In the case of changes to API output \(which is almost guaranteed to happen over time\) or a minor mistake in jsonschema definition, data syncs could thus break because of mismatched datatype schemas.

To remain robust in operation, the CDK provides a transformation ability to perform automatic object mutation to align with desired schema before outputting to the destination. All streams inherited from airbyte*cdk.sources.streams.core.Stream class have this transform configuration available. It is \_disabled* by default and can be configured per stream within a source connector.

### Default type transformation

Here's how you can configure the TypeTransformer:

```python
from airbyte_cdk.sources.utils.transform import TransformConfig, Transformer
from airbyte_cdk.sources.streams.core import Stream

class MyStream(Stream):
    ...
    transformer = Transformer(TransformConfig.DefaultSchemaNormalization)
    ...
```

In this case default transformation will be applied. For example if you have schema like this

```javascript
{"type": "object", "properties": {"value": {"type": "string"}}}
```

and source API returned object with non-string type, it would be casted to string automaticaly:

```javascript
{"value": 12} -> {"value": "12"}
```

Also it works on complex types:

```javascript
{"value": {"unexpected_object": "value"}} -> {"value": "{'unexpected_object': 'value'}"}
```

And objects inside array of referenced by $ref attribute.

If the value cannot be cast \(e.g. string "asdf" cannot be casted to integer\), the field would retain its original value. Schema type transformation support any jsonschema types, nested objects/arrays and reference types. Types described as array of more than one type \(except "null"\), types under oneOf/anyOf keyword wont be transformed.

_Note:_ This transformation is done by the source, not the stream itself. I.e. if you have overriden "read_records" method in your stream it wont affect object transformation. All transformation are done in-place by modifing output object before passing it to "get_updated_state" method, so "get_updated_state" would receive the transformed object.

### Custom schema type transformation

Default schema type transformation performs simple type casting. Sometimes you want to perform more sophisticated transform like making "date-time" field compliant to rcf3339 standard. In this case you can use custom schema type transformation:

```python
class MyStream(Stream):
    ...
    transformer = Transformer(TransformConfig.CustomSchemaNormalization)
    ...

    @transformer.registerCustomTransform
    def transform_function(original_value: Any, field_schema: Dict[str, Any]) -> Any:
        # transformed_value = ...
        return transformed_value
```

Where original_value is initial field value and field_schema is part of jsonschema describing field type. For schema

```javascript
{"type": "object", "properties": {"value": {"type": "string", "format": "date-time"}}}
```

field_schema variable would be equal to

```javascript
{"type": "string", "format": "date-time"}
```

In this case default transformation would be skipped and only custom transformation apply. If you want to run both default and custom transformation you can configure transdormer object by combining config flags:

```python
transformer = Transformer(TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization)
```

In this case custom transformation will be applied after default type transformation function. Note that order of flags doesn't matter, default transformation will always be run before custom.

In some specific cases, you might want to make your custom transform not static, e.g. Formatting a field according to the connector configuration.
To do so, we suggest you to declare a function to generate another, a.k.a a closure:

```python
class MyStream(Stream):
    ...
    transformer = TypeTransformer(TransformConfig.CustomSchemaNormalization)
    ...
    def __init__(self, config_based_date_format):
        self.config_based_date_format = config_based_date_format
        transform_function = self.get_custom_transform()
        self.transformer.registerCustomTransform(transform_function)

    def get_custom_transform(self):
        def custom_transform_function(original_value, field_schema):
            if original_value and "format" in field_schema and field_schema["format"] == "date":
                transformed_value = pendulum.from_format(original_value, self.config_based_date_format).to_date_string()
                return transformed_value
            return original_value
        return custom_transform_function
```

### Performance consideration

Transforming each object on the fly would add some time for each object processing. This time is depends on object/schema complexity and hardware configuration.

There are some performance benchmarks we've done with ads_insights facebook schema \(it is complex schema with objects nested inside arrays ob object and a lot of references\) and example object. Here is the average transform time per single object, seconds:

```text
regular transform:
0.0008423403530008121

transform without type casting (but value still being write to dict/array):
0.000776215762666349

transform without actual value setting  (but iterating through object properties):
0.0006788729513330812

just traverse/validate through json schema and object fields:
0.0006139181846665452
```

On my PC \(AMD Ryzen 7 5800X\) it took 0.8 milliseconds per object. As you can see most time \(~ 75%\) is taken by jsonschema traverse/validation routine and very little \(less than 10 %\) by actual converting. Processing time can be reduced by skipping jsonschema type checking but it would be no warnings about possible object jsonschema inconsistency.
