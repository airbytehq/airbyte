Module airbyte_cdk.sources.utils.transform
==========================================

Classes
-------

`TransformConfig(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   TypeTransformer class config. Configs can be combined using bitwise or operator e.g.
        ```
        TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization
        ```

    ### Ancestors (in MRO)

    * enum.Flag
    * enum.Enum

    ### Class variables

    `CustomSchemaNormalization`
    :

    `DefaultSchemaNormalization`
    :

    `NoTransform`
    :

`TypeTransformer(config: airbyte_cdk.sources.utils.transform.TransformConfig)`
:   Class for transforming object before output.
    
    Initialize TypeTransformer instance.
    :param config Transform config that would be applied to object

    ### Static methods

    `default_convert(original_item: Any, subschema: Dict[str, Any]) ‑> Any`
    :   Default transform function that is used when TransformConfig.DefaultSchemaNormalization flag set.
        :param original_item original value of field.
        :param subschema part of the jsonschema containing field type/format data.
        :return transformed field value.

    ### Methods

    `registerCustomTransform(self, normalization_callback: Callable[[Any, Dict[str, Any]], Any]) ‑> Callable`
    :   Register custom normalization callback.
        :param normalization_callback function to be used for value
        normalization. Takes original value and part type schema. Should return
        normalized value. See docs/connector-development/cdk-python/schemas.md
        for details.
        :return Same callbeck, this is usefull for using registerCustomTransform function as decorator.

    `transform(self, record: Dict[str, Any], schema: Mapping[str, Any])`
    :   Normalize and validate according to config.
        :param record: record instance for normalization/transformation. All modification are done by modifying existent object.
        :param schema: object's jsonschema for normalization.