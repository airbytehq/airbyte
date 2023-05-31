#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from deepdiff import DeepDiff
from enum import Enum
import jsonschema

from hypothesis import HealthCheck, Verbosity, given, settings
from hypothesis_jsonschema import from_schema

from airbyte_cdk.models import ConnectorSpecification
from connector_acceptance_test.utils import SecretDict
from typing import Dict, Any


class BackwardIncompatibilityContext(Enum):
    SPEC = 1
    DISCOVER = 2


class NonBackwardCompatibleError(Exception):
    def __init__(self, error_message: str, context: BackwardIncompatibilityContext) -> None:
        self.error_message = error_message
        self.context = context
        super().__init__(error_message)

    def __str__(self):
        return f"{self.context} - {self.error_message}"


class BaseDiffChecker(ABC):
    def __init__(self, previous: dict, current: dict) -> None:
        self._previous = previous
        self._current = current
        self.compute_diffs()

    def _raise_error(self, message: str, diff: DeepDiff):
        raise NonBackwardCompatibleError(f"{message}. Diff: {diff.pretty()}", self.context)

    @property
    @abstractmethod
    def context(self):  # pragma: no cover
        pass

    @abstractmethod
    def compute_diffs(self):  # pragma: no cover
        pass

    @abstractmethod
    def assert_is_backward_compatible(self):  # pragma: no cover
        pass

    def check_if_value_of_type_field_changed(self, diff: DeepDiff):
        """Check if a type was changed on a property"""
        # Detect type value change in case type field is declared as a string (e.g "str" -> "int"):
        changes_on_property_type = [
            change for change in diff.get("values_changed", []) if {"properties", "type"}.issubset(change.path(output_format="list"))
        ]
        if changes_on_property_type:
            self._raise_error("The'type' field value was changed.", diff)

    def check_if_new_type_was_added(self, diff: DeepDiff):  # pragma: no cover
        """Detect type value added to type list if new type value is not None (e.g ["str"] -> ["str", "int"])"""
        new_values_in_type_list = [
            change
            for change in diff.get("iterable_item_added", [])
            if change.path(output_format="list")[-2] == "type"
            if change.t2 != "null"
        ]
        if new_values_in_type_list:
            self._raise_error("A new value was added to a 'type' field")

    def check_if_type_of_type_field_changed(self, diff: DeepDiff, allow_type_widening: bool = False):
        """
        Detect the change of type of a type field on a property
        e.g:
        - "str" -> ["str"] VALID
        - "str" -> ["str", "null"] VALID
        - "str" -> ["str", "int"] VALID
        - "str" -> 1 INVALID
        - ["str"] -> "str" VALID
        - ["str"] -> "int" INVALID
        - ["str"] -> 1 INVALID
        """
        type_changes = [
            change for change in diff.get("type_changes", []) if {"properties", "type"}.issubset(change.path(output_format="list"))
        ]
        for change in type_changes:
            # We only accept change on the type field if the new type for this field is list or string
            # This might be something already guaranteed by JSON schema validation.
            if isinstance(change.t1, str):
                if not isinstance(change.t2, list):
                    self._raise_error("A 'type' field was changed from string to an invalid value.", diff)
                if allow_type_widening:
                    # If the new type field is a list we want to make sure it contains the original type (t1):
                    # e.g. "str" -> ["str", "null"]
                    #      "int" -> ["int", "str"]
                    # We want to raise an error otherwise.
                    if change.t1 not in change.t2:
                        self._raise_error("The 'type' field was changed to a list which does not contain previous type", diff)
                else:
                    # If the new type field is a list we want to make sure it only has the original type (t1)
                    # and null: e.g. "str" -> ["str", "null"]
                    # We want to raise an error otherwise.
                    t2_not_null_types = [_type for _type in change.t2 if _type != "null"]
                    if not (len(t2_not_null_types) == 1 and t2_not_null_types[0] == change.t1):
                        self._raise_error("The 'type' field was changed to a list with multiple invalid values", diff)
            if isinstance(change.t1, list):
                if not isinstance(change.t2, str):
                    self._raise_error("The 'type' field was changed from a list to an invalid value", diff)
                if not (len(change.t1) == 1 and change.t2 == change.t1[0]):
                    self._raise_error("An element was removed from the list of 'type'", diff)


class SpecDiffChecker(BaseDiffChecker):
    """A class to perform backward compatibility checks on a connector specification diff"""

    context = BackwardIncompatibilityContext.SPEC

    def compute_diffs(self):
        self.connection_specification_diff = DeepDiff(
            self._previous["connectionSpecification"],
            self._current["connectionSpecification"],
            view="tree",
            ignore_order=True,
        )

    def assert_is_backward_compatible(self):
        self.check_if_declared_new_required_field(self.connection_specification_diff)
        self.check_if_added_a_new_required_property(self.connection_specification_diff)
        self.check_if_value_of_type_field_changed(self.connection_specification_diff)
        # self.check_if_new_type_was_added(self.connection_specification_diff) We want to allow type expansion atm
        self.check_if_type_of_type_field_changed(self.connection_specification_diff, allow_type_widening=True)
        self.check_if_field_was_made_not_nullable(self.connection_specification_diff)
        self.check_if_enum_was_narrowed(self.connection_specification_diff)
        self.check_if_declared_new_enum_field(self.connection_specification_diff)

    def check_if_declared_new_required_field(self, diff: DeepDiff):
        """Check if the new spec declared a 'required' field."""
        added_required_fields = [
            addition for addition in diff.get("dictionary_item_added", []) if addition.path(output_format="list")[-1] == "required"
        ]
        if added_required_fields:
            self._raise_error("A new 'required' field was declared.", diff)

    def check_if_added_a_new_required_property(self, diff: DeepDiff):
        """Check if the new spec added a property to the 'required' list"""
        added_required_properties = [
            addition for addition in diff.get("iterable_item_added", []) if addition.up.path(output_format="list")[-1] == "required"
        ]
        if added_required_properties:
            self._raise_error("A new property was added to 'required'", diff)

    def check_if_field_was_made_not_nullable(self, diff: DeepDiff):
        """Detect when field was made not nullable but is still a list: e.g ["string", "null"] -> ["string"]"""
        removed_nullable = [
            change for change in diff.get("iterable_item_removed", []) if {"properties", "type"}.issubset(change.path(output_format="list"))
        ]
        if removed_nullable:
            self._raise_error("A field type was narrowed or made a field not nullable", diff)

    def check_if_enum_was_narrowed(self, diff: DeepDiff):
        """Check if the list of values in a enum was shortened in a spec."""
        enum_removals = [
            enum_removal
            for enum_removal in diff.get("iterable_item_removed", [])
            if enum_removal.up.path(output_format="list")[-1] == "enum"
        ]
        if enum_removals:
            self._raise_error("An enum field was narrowed.", diff)

    def check_if_declared_new_enum_field(self, diff: DeepDiff):
        """Check if an 'enum' field was added to the spec."""
        enum_additions = [
            enum_addition
            for enum_addition in diff.get("dictionary_item_added", [])
            if enum_addition.path(output_format="list")[-1] == "enum"
        ]
        if enum_additions:
            self._raise_error("An 'enum' field was declared on an existing property", diff)


def remove_date_time_pattern_format(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    This function traverses a JSON schema and removes the 'format' field for properties
    that are of 'date-time' format and have a 'pattern' field.

    The 'pattern' is often more restrictive than the 'date-time' format, and Hypothesis can't natively generate
    date-times that match a specific pattern. Therefore, in this case, we've opted to
    remove the 'date-time' format since the 'pattern' is more restrictive and more likely
    to cause a breaking change if not adhered to.

    On the otherside we also validate the output of hypothesis against the new schema to ensure
    that the generated data matches the new schema. In this case we will catch whether or not the
    date-time format is still being adhered to.

    Args:
        schema (Dict[str, Any]): The JSON schema to be processed.

    Returns:
        Dict[str, Any]: The processed JSON schema where 'date-time' format has been removed
                        for properties that have a 'pattern'.
    """
    if isinstance(schema, dict):
        for key, value in schema.items():
            if isinstance(value, dict):
                if value.get('format') == 'date-time' and 'pattern' in value:
                    del value['format']
                remove_date_time_pattern_format(value)
    return schema


def validate_previous_configs(
    previous_connector_spec: ConnectorSpecification, actual_connector_spec: ConnectorSpecification, number_of_configs_to_generate=100
):
    """Use hypothesis and hypothesis-jsonschema to run property based testing:
    1. Generate fake previous config with the previous connector specification json schema.
    2. Validate a fake previous config against the actual connector specification json schema."""
    prev_con_spec = previous_connector_spec.dict()["connectionSpecification"]
    @given(from_schema(remove_date_time_pattern_format(prev_con_spec)))
    @settings(
        max_examples=number_of_configs_to_generate,
        verbosity=Verbosity.verbose,
        suppress_health_check=(HealthCheck.too_slow, HealthCheck.filter_too_much),
    )
    def check_fake_previous_config_against_actual_spec(fake_previous_config):
        if isinstance(fake_previous_config, dict):  # Looks like hypothesis-jsonschema not only generate dict objects...
            fake_previous_config = SecretDict(fake_previous_config)
            filtered_fake_previous_config = {key: value for key, value in fake_previous_config.data.items() if not key.startswith("_")}
            try:
                jsonschema.validate(instance=filtered_fake_previous_config, schema=actual_connector_spec.connectionSpecification)
            except jsonschema.exceptions.ValidationError as err:
                raise NonBackwardCompatibleError(err, BackwardIncompatibilityContext.SPEC)

    check_fake_previous_config_against_actual_spec()


class CatalogDiffChecker(BaseDiffChecker):
    """A class to perform backward compatibility checks on a discoverd catalog diff"""

    context = BackwardIncompatibilityContext.DISCOVER

    def compute_diffs(self):
        self.streams_json_schemas_diff = DeepDiff(
            {stream_name: airbyte_stream.dict().pop("json_schema") for stream_name, airbyte_stream in self._previous.items()},
            {stream_name: airbyte_stream.dict().pop("json_schema") for stream_name, airbyte_stream in self._current.items()},
            view="tree",
            ignore_order=True,
        )
        self.streams_cursor_fields_diff = DeepDiff(
            {stream_name: airbyte_stream.dict().pop("default_cursor_field") for stream_name, airbyte_stream in self._previous.items()},
            {stream_name: airbyte_stream.dict().pop("default_cursor_field") for stream_name, airbyte_stream in self._current.items()},
            view="tree",
        )

    def assert_is_backward_compatible(self):
        self.check_if_stream_was_removed(self.streams_json_schemas_diff)
        self.check_if_value_of_type_field_changed(self.streams_json_schemas_diff)
        self.check_if_type_of_type_field_changed(self.streams_json_schemas_diff, allow_type_widening=False)
        self.check_if_cursor_field_was_changed(self.streams_cursor_fields_diff)

    def check_if_stream_was_removed(self, diff: DeepDiff):
        """Check if a stream was removed from the catalog."""
        removed_streams = []
        for removal in diff.get("dictionary_item_removed", []):
            if removal.path() != "root" and removal.up.path() == "root":
                removed_streams.append(removal.path(output_format="list")[0])
        if removed_streams:
            self._raise_error(f"The following streams were removed: {','.join(removed_streams)}", diff)

    def check_if_cursor_field_was_changed(self, diff: DeepDiff):
        """Check if a default cursor field value was changed."""
        invalid_changes = {"values_changed", "iterable_item_added", "iterable_item_removed"}
        if any([change in invalid_changes for change in diff.keys()]):
            self._raise_error("The value of 'default_cursor_field' was changed", diff)
