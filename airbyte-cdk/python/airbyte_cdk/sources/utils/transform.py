#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from enum import Flag, auto
from typing import Any, Callable, Dict

from jsonschema import Draft7Validator, validators


class TransformConfig(Flag):
    """
    Transformer class config. Configs can be combined using bitwise or operator e.g.
        ```
        TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization
        ```
    """

    NoTransform = auto()
    DefaultSchemaNormalization = auto()
    CustomSchemaNormalization = auto()
    # TODO: implement field transformation with user defined object path
    FieldTransformation = auto()


class Transformer:
    """
    Class for transforming object before output.
    """

    _custom_normalizer: Callable[[Any, Dict[str, Any]], Any] = None

    def __init__(self, config: TransformConfig):
        """
        Initialize Transformer instance.
        :param config Transform config that would be applied to object
        """
        if TransformConfig.NoTransform in config and config != TransformConfig.NoTransform:
            raise Exception("NoTransform option cannot be combined with other flags.")
        self._config = config
        all_validators = {
            key: self.__normalize_and_validate(key, orig_validator)
            for key, orig_validator in Draft7Validator.VALIDATORS.items()
            # Do not validate field we do not transform for maximum performance.
            if key in ["type", "array", "$ref", "properties", "items"]
        }
        self._normalizer = validators.create(meta_schema=Draft7Validator.META_SCHEMA, validators=all_validators)

    def register(self, normalization_callback: Callable) -> Callable:
        """
        Register custom normalization callback.
        :param normalization_callback function to be used for value
        normalization. Should return normalized value.
        :return Same callbeck, this is usefull for using register function as decorator.
        """
        if TransformConfig.CustomSchemaNormalization not in self._config:
            raise Exception("Please set TransformConfig.CustomSchemaNormalization config before registering custom normalizer")
        self._custom_normalizer = normalization_callback
        return normalization_callback

    def __normalize(self, original_item: Any, subschema: Dict[str, Any]) -> Any:
        """
        Applies different transform function to object's field according to config.
        :param original_item original value of field.
        :param subschema part of the jsonschema containing field type/format data.
        :return Final field value.
        """
        if TransformConfig.DefaultSchemaNormalization in self._config:
            original_item = self.default_convert(original_item, subschema)

        if self._custom_normalizer:
            original_item = self._custom_normalizer(original_item, subschema)
        return original_item

    @staticmethod
    def default_convert(original_item: Any, subschema: Dict[str, Any]) -> Any:
        """
        Default transform function that is used when TransformConfig.DefaultSchemaNormalization flag set.
        :param original_item original value of field.
        :param subschema part of the jsonschema containing field type/format data.
        :return transformed field value.
        """
        target_type = subschema.get("type")
        if original_item is None and "null" in target_type:
            return None
        if isinstance(target_type, list):
            target_type = [t for t in target_type if t != "null"]
            if len(target_type) != 1:
                return original_item
            target_type = target_type[0]
        try:
            if target_type == "string":
                return str(original_item)
            elif target_type == "number":
                return float(original_item)
            elif target_type == "integer":
                return int(original_item)
            elif target_type == "boolean":
                return bool(original_item)
        except ValueError:
            return original_item
        return original_item

    def __normalize_and_validate(self, schema_key: str, original_validator: Callable):
        """
        Traverse through object fields using native jsonschema validator and apply normalization function.
        :param schema_key related json schema key that currently being validated/normalized.
        :original_validator: native jsonschema validator callback.
        """

        def normalizator(validator_instance, val, instance, schema):
            def resolve(subschema):
                if "$ref" in subschema:
                    _, resolved = validator_instance.resolver.resolve(subschema["$ref"])
                    return resolved
                return subschema

            if schema_key == "type" and instance is not None:
                if "object" in val and isinstance(instance, dict):
                    for k, subschema in schema.get("properties", {}).items():
                        if k in instance:
                            subschema = resolve(subschema)
                            instance[k] = self.__normalize(instance[k], subschema)
                elif "array" in val and isinstance(instance, list):
                    subschema = schema.get("items", {})
                    subschema = resolve(subschema)
                    for index, item in enumerate(instance):
                        instance[index] = self.__normalize(item, subschema)
            # Running native jsonschema traverse algorithm after field normalization is done.
            yield from original_validator(validator_instance, val, instance, schema)

        return normalizator

    def transform(self, instance: Dict[str, Any], schema: Dict[str, Any]):
        """
        Normalize and validate according to config.
        :param instance object instance for normalization/transformation. All modification are done by modifing existent object.
        :schema object's jsonschema for normalization.
        """
        if TransformConfig.NoTransform in self._config:
            return
        normalizer = self._normalizer(schema)
        for e in normalizer.iter_errors(instance):
            """
            just calling normalizer.validate() would throw an exception on
            first validation occurences and stop processing rest of schema.
            """
            # TODO: log warning
