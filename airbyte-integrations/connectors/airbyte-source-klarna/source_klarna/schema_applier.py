import hashlib
from typing import Mapping, Any, Union, Iterable, Optional

# noinspection PyPackageRequirements
from jsonschema.validators import validate


class SchemaApplier:
    """
    Class that can hash, exclude or make blank (empty) dictionary fields based on provided json schema custom keywords
    available custom keywords are:
    - "empty"  - if set to "true" value of given primitive property (not whole 'array' nor 'object') will be set to
                empty string
    - "hashed" - if empty is not set to "true" the value of given primitive property (not whole 'array' nor 'object')
                will be hashed using sha3-512 with provided to constructor cryptographic salt

    Known limitations:
     - not supporting multi types in array nor in single field
        ...
        "prop": {"type": "array", "items": [{"type":"integer"}, {"type":"string"}]}
        or simply
        "prop": {"type": ["string", "null"]}
        ...
    """

    def __init__(self, salt: bytes, remove_missing: bool = True):
        self.salt = salt
        self.remove_missing = remove_missing

    def apply_schema_transformations(self, instance, schema) -> Iterable[Mapping]:
        validate(instance=instance, schema=schema)
        return self.__map_generic(instance, schema)

    @staticmethod
    def __apply_func(elem: Union[str, int, bool], schema: Mapping[str, Any], salt: bytes) -> Union[str, int, bool]:
        if schema.get('empty', None):
            return ""
        if schema.get('hashed', None):
            hash_func = hashlib.sha3_512()
            hash_func.update(salt + str(elem).encode())
            return hash_func.hexdigest()
        return elem

    def __map_generic(self, value, schema: Mapping[str, Any]) -> Optional[Iterable]:
        elem_type = schema.get('type', None)
        if not elem_type:
            return

        if elem_type == 'object':
            new_obj = {}
            new_schema = schema.get('properties', None)
            if not new_schema:
                return new_obj
            for k, v in value.items():
                try:
                    new_obj[k] = self.__map_generic(v, new_schema[k])
                except KeyError:
                    if not self.remove_missing:
                        new_obj[k] = v
            return new_obj
        elif elem_type == 'array':
            new_array = []
            new_schema = schema.get('items', None)
            if not new_schema:
                return new_array
            for e in value:
                new_array.append(self.__map_generic(e, new_schema))
            return new_array
        else:
            return SchemaApplier.__apply_func(value, schema, self.salt)
