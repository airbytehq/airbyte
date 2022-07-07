Module airbyte_cdk.sources.declarative.schema.json_schema
=========================================================

Classes
-------

`JsonSchema(file_path: Union[str, airbyte_cdk.sources.declarative.interpolation.interpolated_string.InterpolatedString], config, **kwargs)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.declarative.schema.schema_loader.SchemaLoader
    * abc.ABC

    ### Methods

    `get_json_schema(self) ‑> Mapping[str, Any]`
    :