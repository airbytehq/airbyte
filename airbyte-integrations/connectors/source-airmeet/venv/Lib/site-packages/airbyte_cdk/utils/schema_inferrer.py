#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from collections import defaultdict
from typing import Any, Dict, List, Mapping, Optional

from genson import SchemaBuilder, SchemaNode
from genson.schema.strategies.object import Object
from genson.schema.strategies.scalar import Number

from airbyte_cdk.models import AirbyteRecordMessage

# schema keywords
_TYPE = "type"
_NULL_TYPE = "null"
_OBJECT_TYPE = "object"
_ANY_OF = "anyOf"
_ITEMS = "items"
_PROPERTIES = "properties"
_REQUIRED = "required"


class NoRequiredObj(Object):
    """
    This class has Object behaviour, but it does not generate "required[]" fields
    every time it parses object. So we don't add unnecessary extra field.

    The logic is that even reading all the data from a source, it does not mean that there can be another record added with those fields as
    optional. Hence, we make everything nullable.
    """

    def to_schema(self) -> Mapping[str, Any]:
        schema: Dict[str, Any] = super(NoRequiredObj, self).to_schema()
        schema.pop("required", None)
        return schema


class IntegerToNumber(Number):
    """
    This class has the regular Number behaviour, but it will never emit an integer type.
    """

    def __init__(self, node_class: SchemaNode):
        super().__init__(node_class)
        self._type = "number"


class NoRequiredSchemaBuilder(SchemaBuilder):
    EXTRA_STRATEGIES = (NoRequiredObj, IntegerToNumber)


# This type is inferred from the genson lib, but there is no alias provided for it - creating it here for type safety
InferredSchema = Dict[str, Any]


class SchemaValidationException(Exception):
    @classmethod
    def merge_exceptions(
        cls, exceptions: List["SchemaValidationException"]
    ) -> "SchemaValidationException":
        # We assume the schema is the same for all SchemaValidationException
        return SchemaValidationException(
            exceptions[0].schema,
            [x for exception in exceptions for x in exception._validation_errors],
        )

    def __init__(self, schema: InferredSchema, validation_errors: List[Exception]):
        self._schema = schema
        self._validation_errors = validation_errors

    @property
    def schema(self) -> InferredSchema:
        return self._schema

    @property
    def validation_errors(self) -> List[str]:
        return list(map(lambda error: str(error), self._validation_errors))


class SchemaInferrer:
    """
    This class is used to infer a JSON schema which fits all the records passed into it
    throughout its lifecycle via the accumulate method.

    Instances of this class are stateful, meaning they build their inferred schemas
    from every record passed into the accumulate method.

    """

    stream_to_builder: Dict[str, SchemaBuilder]

    def __init__(
        self, pk: Optional[List[List[str]]] = None, cursor_field: Optional[List[List[str]]] = None
    ) -> None:
        self.stream_to_builder = defaultdict(NoRequiredSchemaBuilder)
        self._pk = [] if pk is None else pk
        self._cursor_field = [] if cursor_field is None else cursor_field

    def accumulate(self, record: AirbyteRecordMessage) -> None:
        """Uses the input record to add to the inferred schemas maintained by this object"""
        self.stream_to_builder[record.stream].add_object(record.data)

    def _null_type_in_any_of(self, node: InferredSchema) -> bool:
        if _ANY_OF in node:
            return {_TYPE: _NULL_TYPE} in node[_ANY_OF]
        else:
            return False

    def _remove_type_from_any_of(self, node: InferredSchema) -> None:
        if _ANY_OF in node:
            node.pop(_TYPE, None)

    def _clean_any_of(self, node: InferredSchema) -> None:
        if len(node[_ANY_OF]) == 2 and self._null_type_in_any_of(node):
            real_type = (
                node[_ANY_OF][1] if node[_ANY_OF][0][_TYPE] == _NULL_TYPE else node[_ANY_OF][0]
            )
            node.update(real_type)
            node[_TYPE] = [node[_TYPE], _NULL_TYPE]
            node.pop(_ANY_OF)
        # populate `type` for `anyOf` if it's not present to pass all other checks
        elif len(node[_ANY_OF]) == 2 and not self._null_type_in_any_of(node):
            node[_TYPE] = [_NULL_TYPE]

    def _clean_properties(self, node: InferredSchema) -> None:
        for key, value in list(node[_PROPERTIES].items()):
            if isinstance(value, dict) and value.get(_TYPE, None) == _NULL_TYPE:
                node[_PROPERTIES].pop(key)
            else:
                self._clean(value)

    def _ensure_null_type_on_top(self, node: InferredSchema) -> None:
        if isinstance(node[_TYPE], list):
            if _NULL_TYPE in node[_TYPE]:
                # we want to make sure null is always at the end as it makes schemas more readable
                node[_TYPE].remove(_NULL_TYPE)
            node[_TYPE].append(_NULL_TYPE)
        else:
            node[_TYPE] = [node[_TYPE], _NULL_TYPE]

    def _clean(self, node: InferredSchema) -> InferredSchema:
        """
        Recursively cleans up a produced schema:
        - remove anyOf if one of them is just a null value
        - remove properties of type "null"
        """

        if isinstance(node, dict):
            if _ANY_OF in node:
                self._clean_any_of(node)

            if _PROPERTIES in node and isinstance(node[_PROPERTIES], dict):
                self._clean_properties(node)

            if _ITEMS in node:
                self._clean(node[_ITEMS])

            # this check needs to follow the "anyOf" cleaning as it might populate `type`
            self._ensure_null_type_on_top(node)

        # remove added `type: ["null"]` for `anyOf` nested node
        self._remove_type_from_any_of(node)

        return node

    def _add_required_properties(self, node: InferredSchema) -> InferredSchema:
        """
        This method takes properties that should be marked as required (self._pk and self._cursor_field) and travel the schema to mark every
        node as required.
        """
        # Removing nullable for the root as when we call `_clean`, we make everything nullable
        node[_TYPE] = _OBJECT_TYPE

        exceptions = []
        for field in [x for x in [self._pk, self._cursor_field] if x]:
            try:
                self._add_fields_as_required(node, field)
            except SchemaValidationException as exception:
                exceptions.append(exception)

        if exceptions:
            raise SchemaValidationException.merge_exceptions(exceptions)

        return node

    def _add_fields_as_required(self, node: InferredSchema, composite_key: List[List[str]]) -> None:
        """
        Take a list of nested keys (this list represents a composite key) and travel the schema to mark every node as required.
        """
        errors: List[Exception] = []

        for path in composite_key:
            try:
                self._add_field_as_required(node, path)
            except ValueError as exception:
                errors.append(exception)

        if errors:
            raise SchemaValidationException(node, errors)

    def _add_field_as_required(
        self, node: InferredSchema, path: List[str], traveled_path: Optional[List[str]] = None
    ) -> None:
        """
        Take a nested key and travel the schema to mark every node as required.
        """
        self._remove_null_from_type(node)
        if self._is_leaf(path):
            return

        if not traveled_path:
            traveled_path = []

        if _PROPERTIES not in node:
            # This validation is only relevant when `traveled_path` is empty
            raise ValueError(
                f"Path {traveled_path} does not refer to an object but is `{node}` and hence {path} can't be marked as required."
            )

        next_node = path[0]
        if next_node not in node[_PROPERTIES]:
            raise ValueError(
                f"Path {traveled_path} does not have field `{next_node}` in the schema and hence can't be marked as required."
            )

        if _TYPE not in node:
            # We do not expect this case to happen but we added a specific error message just in case
            raise ValueError(
                f"Unknown schema error: {traveled_path} is expected to have a type but did not. Schema inferrence is probably broken"
            )

        if node[_TYPE] not in [
            _OBJECT_TYPE,
            [_NULL_TYPE, _OBJECT_TYPE],
            [_OBJECT_TYPE, _NULL_TYPE],
        ]:
            raise ValueError(
                f"Path {traveled_path} is expected to be an object but was of type `{node['properties'][next_node]['type']}`"
            )

        if _REQUIRED not in node or not node[_REQUIRED]:
            node[_REQUIRED] = [next_node]
        elif next_node not in node[_REQUIRED]:
            node[_REQUIRED].append(next_node)

        traveled_path.append(next_node)
        self._add_field_as_required(node[_PROPERTIES][next_node], path[1:], traveled_path)

    def _is_leaf(self, path: List[str]) -> bool:
        return len(path) == 0

    def _remove_null_from_type(self, node: InferredSchema) -> None:
        if isinstance(node[_TYPE], list):
            if _NULL_TYPE in node[_TYPE]:
                node[_TYPE].remove(_NULL_TYPE)
            if len(node[_TYPE]) == 1:
                node[_TYPE] = node[_TYPE][0]

    def get_stream_schema(self, stream_name: str) -> Optional[InferredSchema]:
        """
        Returns the inferred JSON schema for the specified stream. Might be `None` if there were no records for the given stream name.
        """
        return (
            self._add_required_properties(
                self._clean(self.stream_to_builder[stream_name].to_schema())
            )
            if stream_name in self.stream_to_builder
            else None
        )
