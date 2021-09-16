# Defining your stream schemas
Your connector must describe the schema of each stream it can output using [JSONSchema](https://json-schema.org). 

The simplest way to do this is to describe the schema of your streams using one `.json` file per stream. You can also dynamically generate the schema of your stream in code, or you can combine both approaches: start with a `.json` file and dynamically add properties to it. 
 
The schema of a stream is the return value of `Stream.get_json_schema`.
 
## Static schemas
By default, `Stream.get_json_schema` reads a `.json` file in the `schemas/` directory whose name is equal to the value of the `Stream.name` property. In turn `Stream.name` by default returns the name of the class in snake case. Therefore, if you have a class `class EmployeeBenefits(HttpStream)` the default behavior will look for a file called `schemas/employee_benefits.json`. You can override any of these behaviors as you need.

Important note: any objects referenced via `$ref` should be placed in the `shared/` directory in their own `.json` files.

### Generating schemas from OpenAPI definitions
If you are implementing a connector to pull data from an API which publishes an [OpenAPI/Swagger spec](https://swagger.io/specification/), you can use a tool we've provided for generating JSON schemas from the OpenAPI definition file. Detailed information can be found [here](https://github.com/airbytehq/airbyte/tree/master/tools/openapi2jsonschema/).
 
## Dynamic schemas
If you'd rather define your schema in code, override `Stream.get_json_schema` in your stream class to return a `dict` describing the schema using [JSONSchema](https://json-schema.org).

## Dynamically modifying static schemas    
Override `Stream.get_json_schema` to run the default behavior, edit the returned value, then return the edited value: 
```
def get_json_schema(self):
    schema = super().get_json_schema()
    schema['dynamically_determined_property'] = "property"
    return schema
```

## Schema normalization

Complying output data  to declared json schema is important because those data later could be used by destination that rely on received data types (e.g. when data is stored in SQL database and you can't put INTEGER type into CHAR column and so on). In case of minor jsonschema mistake or API change could break synchronization process even if data fetching completed successfully.

To handle this cases CDK provides ability to perform automatic object tranformation before output it to destination controller. All streams inherited from airbyte_cdk.sources.streams.core.Stream class have transform confgiuration that able to perform operation on individual object's field value. By default it do no changes and can be reconfigured in user's streams.
### Default schema normalization
Lets say you want have output records from controller to be casted to the type described on json schema. This is how you can configure it:

```python
from airbyte_cdk.sources.utils.transform import TransformConfig, Transformer
from airbyte_cdk.sources.streams.core import Stream

class MyStream(Stream):
    ...
    transformer = Transformer(TransformConfig.DefaultSchemaNormalization)
    ...
```
In this case default transformation will be applied. For example if you have schema like this
```json
{"type": "object", "properties": {"value": {"type": "string"}}}
```
and source API returned object with non-string type, it would be casted to string automaticaly:
```json
{"value": 12} -> {"value": "12"}
```
Also it works on complex types:
```json
{"value": {"unexpected_object": "value"}} -> {"value": "{'unexpected_object': 'value'}"}
```
And objects inside array of referenced by $ref attribute.

 In case if value cannot be casted (e.g. string "asdf" cannot be casted to integer) field would contain original value and no error reported.

*Note:* This transformation is done by source, not stream itself. I.e. if you have overriden "read_records" method in your stream it wont affect object transformation. All transformation are done in-place by modifing output object before passing it to "get_updated_state" method, so "get_updated_state" would receive transformed object.

### Custom schema normalization
Default schema normalization perform simple type casting regardless its format. Sometimes you want to perform more sofisticated transform like making "date-time" field compliant to rcf3339 standard. In this case you can use custom schema normalization:
```python
class MyStream(Stream):
    ...
    transformer = Transformer(TransformConfig.CustomSchemaNormalization)
    ...

    @transformer.register
    def transform_function(orginal_value: Any, field_schema: Dict[str, Any]) -> Any:
        # transformed_value = ...
        return transformed_value
```
Where original_value is initial field value and field_schema is part of jsonschema describing field type. For schema
```json
{"type": "object", "properties": {"value": {"type": "string", "format": "date-time"}}}
```
field_schema variable would be equal to
```json
{"type": "string", "format": "date-time"}
```
In this case default normalization would be skipped and only custom transformation apply. If you want to run both default and custom normalization you can configure transdormer object by combining config flags:
```python
transformer = Transformer(TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization)
```
In this case custom normalization will be applied after default normalization function. Note that order of flags doesnt matter, default normalization will always be run before custom.
